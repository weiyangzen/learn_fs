# sources/distributed-fs/ceph-client/arch/x86/kernel/espfix_64.c

## Purpose
Builds the 64-bit ESPFIX alias-stack mapping that prevents 16-bit IRET from truncating RSP and leaking kernel stack bits.

## Important APIs, Types, And Functions
Per-CPU `espfix_stack` and `espfix_waddr` expose alias and writable addresses. `init_espfix_bsp()` installs the PUD and randomization on the boot CPU. `init_espfix_ap()` allocates per-page ministacks and page tables for CPUs. `espfix_base_addr()` computes randomized alias addresses.

## Control Flow
FRED-capable systems skip ESPFIX because FRED restores full RSP. BSP init attaches `espfix_pud_page` under `ESPFIX_BASE_ADDR`, randomizes page/slot selection, then initializes CPU 0. AP init returns if already done, computes the alias, shares one physical page across several CPU ministacks, lazily allocates missing PUD/PMD/PTE levels under a mutex, maps clones 64 KiB apart read-only/global/encrypted, then records readable alias and writable kernel address.

## State, Persistence, And Dependencies
State includes per-CPU stack addresses, `espfix_pages[]`, shared page-table pages, randomization seeds, and kernel page-table entries. It depends on paging constants, CPU node allocation, paravirt page-table allocation hooks, encryption page bits, and entry assembly using the ministack.

## Integration Points
Entry code uses these aliases when returning to 16-bit LDT stack segments. Double-fault handling repairs faults caused by read-only ministacks.

## Risks
Alias math and clone counts must match page-table geometry. Allocation races are protected by a mutex, but page-table initialization must be globally visible. Misconfiguration can break 16-bit compatibility or leak stack addresses.

## Test Signals
16-bit/LDT IRET tests on non-FRED x86_64 should not truncate or leak RSP; CPU hotplug should initialize per-CPU ESPFIX addresses once; FRED systems should skip setup.
