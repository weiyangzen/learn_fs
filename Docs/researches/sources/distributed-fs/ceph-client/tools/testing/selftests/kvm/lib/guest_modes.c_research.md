# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/guest_modes.c

## Purpose
This file manages the list of guest address/page-size modes that a selftest should run. It provides architecture-aware default mode discovery, command-line mode selection, help text, and iteration.

## Important APIs, Types, and Functions
Global `guest_modes[NUM_VM_MODES]` stores support/enabled state. `guest_modes_append_default()` appends supported modes based on architecture capability probing. `for_each_guest_mode()` invokes a callback for enabled modes. `guest_modes_help()` prints supported IDs. `guest_modes_cmdline()` enables explicit mode IDs.

## Control Flow
Non-arm64/riscv architectures append `VM_MODE_DEFAULT`. arm64 probes IPA and page-size support; s390 probes CPU model to add 47-bit mode; RISC-V checks GPA bits and SATP modes. Explicit `-m` selection first disables all modes, then enables requested IDs.

## State, Dependencies, and Integration
State is process-global mode enablement plus `vm_mode_default` on arm64/RISC-V. It depends on architecture probing helpers from `processor.c`, KVM capabilities, and parsing/assert helpers. Test programs like `kvm_page_table_test.c` use it to sweep modes.

## Risks and Test Signals
Incorrect support detection can skip coverage or select unsupported modes. `for_each_guest_mode()` asserts if an enabled mode is unsupported, providing an immediate signal for bad command-line selection or probing errors.
