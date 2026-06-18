# sources/distributed-fs/ceph-client/arch/arm/include/asm/setup.h

## Purpose
Defines ARM boot parameter, machine setup, and command-line interfaces shared by early architecture setup.

## Important APIs, Types, And Functions
Key declarations include extern int arm_add_memory(u64 start, u64 size);; extern __printf(1, 2) void early_print(const char *str, ...);; extern void dump_machine_table(void);; extern void save_atags(const struct tag *tags);; static inline void save_atags(const struct tag *tags) { }; struct machine_desc;. Important macros/constants include __ASMARM_SETUP_H, __tag, __tagtable(tag,. It depends directly on #include <linux/screen_info.h>, #include <uapi/asm/setup.h>.

## Control Flow
Boot code consumes tags or device-tree input, initializes memory and machine descriptors, and exposes setup data to later init code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/screen_info.h>, #include <uapi/asm/setup.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
