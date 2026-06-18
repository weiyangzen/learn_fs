# sources/distributed-fs/ceph-client/arch/s390/kvm/guestdbg.c

## Purpose
Implements s390 KVM guest debugging support using PER controls. It imports userspace hardware breakpoint/watchpoint requests, patches guest PER registers for single-step and hardware debug, filters guest PER events, detects watchpoint changes, and prepares `KVM_EXIT_DEBUG` exits.

## Important APIs, Types, And Functions
Public functions are `kvm_s390_backup_guest_per_regs`, `kvm_s390_restore_guest_per_regs`, `kvm_s390_patch_guest_per_regs`, `kvm_s390_import_bp_data`, `kvm_s390_clear_bp_data`, `kvm_s390_prepare_debug_exit`, `kvm_s390_handle_per_ifetch_icpt`, and `kvm_s390_handle_per_event`. Internal helpers include `extend_address_range`, `enable_all_hw_bp`, `enable_all_hw_wp`, `__import_wp_info`, `find_hw_bp`, `any_wp_changed`, `debug_exit_required`, `per_fetched_addr`, and `filter_guest_per_event`.

## Control Flow
When guest debug is enabled, KVM saves guest CR0/CR9/CR10/CR11, patches PER event/range controls for single-step or requested breakpoints/watchpoints, then restores the guest registers after the debug run window. Userspace breakpoint data is copied from user memory, split into breakpoint and write-watchpoint arrays, and watchpoints keep a backup copy of the original guest physical bytes. PER intercept handling first decides whether a userspace debug exit is required, then filters the remaining PER code so guest-requested PER events are still delivered accurately. Instruction-fetch PER handling rewinds PSW or decodes EXECUTE/EXECUTE RELATIVE LONG to find the actual fetched instruction address.

## State And Persistence
State is per-vCPU runtime debug state: saved control registers, breakpoint/watchpoint arrays, watchpoint `old_data` buffers, last breakpoint address, pending debug-exit flag, and `run->debug.arch` exit metadata. No durable persistence is used.

## Dependencies And Integration Points
Depends on KVM guest debug UAPI, s390 PER control bits, guest memory read helpers from `gaccess.h`, PSW rewind and instruction-length helpers, SIE intercept fields, and the intercept loop in `intercept.c`. It shares PER event filtering with normal guest PER delivery so host debug does not swallow guest-visible events accidentally.

## Risks And Edge Cases
PER ranges may wrap around address zero; `extend_address_range` and `in_addr_range` must handle overflow intervals. Breakpoints widen by up to six bytes to catch the preceding instruction fetch. Watchpoint detection compares memory after the event and can miss failures if reading guest memory fails or allocation for the temporary buffer fails. EXECUTE decoding must compute the executed target correctly. Single-step plus concurrent interrupts is intentionally deferred by intercept logic.

## Test Signals
Use s390 KVM guest-debug tests for single-step, hardware breakpoints, write watchpoints, wrapped address ranges, duplicate PER events, EXECUTE and EXECUTE RELATIVE LONG targets, guest PER passthrough, pending debug exits, and cleanup/reimport cycles with leak detection.
