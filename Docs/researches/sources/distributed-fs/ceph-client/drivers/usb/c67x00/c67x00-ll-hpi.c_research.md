# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-ll-hpi.c

## Purpose
`c67x00-ll-hpi.c` implements the low-level Host Port Interface access layer for Cypress C67X00 controllers. It serializes 16-bit register and memory access, handles mailbox/LCP command transactions, initializes HPI interrupt routing, controls host SIE state, resets ports, and reads/writes controller internal memory.

## Important APIs, Types, And Functions
- `hpi_read_reg()` and `hpi_write_reg()` perform raw HPI register access with the required 125 ns cycle delay.
- `hpi_read_word()`/`hpi_write_word()` and LE16 bulk helpers serialize indexed HPI address/data access under `dev->hpi.lock`.
- `c67x00_ll_hpi_status()`, `c67x00_ll_hpi_reg_init()`, `c67x00_ll_hpi_enable_sofeop()`, and `disable_sofeop()` manage HPI status/routing.
- `c67x00_comm_exec_int()` sends LCP software interrupts through communication registers and waits for mailbox completion.
- Host helpers include `c67x00_ll_husb_init_host_port()`, `reset()`, `reset_port()`, current TD get/set, frame get, USB status get/clear, and EOT setting.
- `c67x00_ll_write_mem_le16()` and `read_mem_le16()` handle aligned and unaligned controller memory transfers.
- `c67x00_ll_irq()` completes LCP mailbox waits on mailbox-out interrupts.

## Control Flow
Initialization sets up mutex/completion state, clears mailbox/status, disables IRQ routing, and clears SIE message registers. Higher layers issue reset or host-port commands through `c67x00_comm_exec_int()`, which writes command registers, sends a mailbox value, and waits up to five seconds for `c67x00_ll_irq()` to complete the transaction. Memory reads/writes use HPI address/data cycles and special-case unaligned first/last bytes.

## State And Persistence Behavior
Persistent runtime state includes HPI spinlock, LCP mutex, last mailbox message, and completion object inside the shared device. Hardware register state includes IRQ routing, host mode, current TD pointer, USB status, EOT, and controller memory contents. No disk persistence exists.

## Dependencies And Integration Points
The file depends on MMIO, delays, completions, mutexes, endian helpers, and C67X00 register definitions from local headers. It is the low-level backend for platform IRQ handling, HCD root-hub operations, and the transfer scheduler.

## Risks And Edge Cases
`BUG_ON(rc)` in host SIE init/reset paths can crash the kernel on LCP timeout. `ll_recv_msg()` warns and returns `-EIO` after timeout, but callers vary in recovery. The file assumes HPI register access is safe in IRQ context and explicitly excludes serial control interfaces. Memory write bounds only check writes beyond `0xffff`; reads do not perform the same explicit bound check. Correct locking between spinlock register access and LCP mutex is critical.

## Test Signals
Probe hardware and verify reset mailbox completion, HPI status clearing, SOF/EOP routing toggles, host port reset, TD pointer writes, frame reads, and unaligned memory read/write round trips. Fault-inject missing mailbox completion to observe timeout handling. Run IRQ-context status and SIE message fetch under load.
