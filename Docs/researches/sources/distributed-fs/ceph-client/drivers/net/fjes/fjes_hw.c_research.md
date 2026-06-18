# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_hw.c

## Purpose
`fjes_hw.c` implements the low-level FJES hardware and shared-memory endpoint protocol. It maps registers, resets the device, allocates command buffers/shared status/endpoint rings, issues device commands, manages endpoint sharing and unsharing, manipulates RX/TX ring metadata, handles zone changes and endpoint stop work, and starts/stops hardware debug tracing.

## Important APIs and Functions
Initialization and teardown are `fjes_hw_init()`, `fjes_hw_exit()`, `fjes_hw_reset()`, and internal `fjes_hw_setup()`/`fjes_hw_cleanup()`. Command APIs are `fjes_hw_request_info()`, `fjes_hw_register_buff_addr()`, `fjes_hw_unregister_buff_addr()`, and `fjes_hw_init_command_registers()`. Interrupt/register helpers are `fjes_hw_rd32()`, `fjes_hw_raise_interrupt()`, `fjes_hw_capture_interrupt_status()`, and `fjes_hw_set_irqmask()`. Endpoint helpers include `fjes_hw_setup_epbuf()`, `fjes_hw_get_partner_ep_status()`, `fjes_hw_epid_is_same_zone()`, `fjes_hw_epid_is_shared()`, stop coordination functions, VLAN/MTU/version checks, RX dequeue helpers, TX enqueue helper, and debug commands.

## Control Flow
`fjes_hw_init()` maps MMIO, resets the device, masks interrupts, initializes work/locks, reads max/local EPIDs, allocates per-endpoint memory, writes command-buffer physical addresses to registers, and allocates the trace buffer. `fjes_hw_setup()` allocates `ep_shm_info`, request/response command buffers, shared status memory, and vmalloc endpoint TX/RX buffers for all remote EPIDs; each ring is initialized with `fjes_hw_setup_epbuf()`.

Device commands fill a request union, clear the response union, write `XSCT_CR`, poll `XSCT_CS` for completion, validate response lengths/codes, map busy/timeouts to errno, and update share bits on success. Zone update work requests current endpoint info, computes share/unshare/interrupt actions, registers buffers for same-zone endpoints, unregisters stale endpoints, or raises TXRX stop requests. Ring TX copies a frame into the tail slot and advances tail; RX reads the head slot and advances head on drop.

## State, Dependencies, and Integration
State lives in `struct fjes_hw`: MMIO base/resource, EPID bounds, endpoint shared memory, shared status region, command buffers, trace buffer, share/unshare bitmasks, stop-request bitmasks, locks, and work items. The file depends on Linux MMIO, vmalloc/page-to-phys translation, workqueues, mutexes/spinlocks, register definitions, tracepoints, and adapter callbacks through `hw->back`.

## Risks and Test Signals
Risks include command timeout handling, vmalloc page physical-address lists, ring-full/empty math, endpoint stop races, zone update forced-close paths, cleanup after partial allocation, and debug trace lifecycle. Test signals should include reset timeout behavior, request-info validation, share/unshare busy retries, same-zone transitions, ring enqueue/dequeue boundaries, MTU/VLAN checks, endpoint stop handshakes, forced reset on command failures, and trace start/stop under lock.
