# sources/distributed-fs/ceph-client/drivers/connector/Makefile

## Purpose
This Makefile maps connector Kconfig symbols to built objects.

## Important APIs, Types, And Functions
`obj-$(CONFIG_CONNECTOR) += cn.o` builds the main connector module/object. `obj-$(CONFIG_PROC_EVENTS) += cn_proc.o` builds process event connector support. `cn-y += cn_queue.o connector.o` links callback queue support and netlink transport into `cn.o`.

## Control Flow
Kbuild includes `cn_queue.o` and `connector.o` in the composite connector object whenever `CONFIG_CONNECTOR` is selected. `cn_proc.o` is separate and only built for process events.

## State And Persistence
No runtime state exists. This file controls build composition only.

## Dependencies And Integration Points
It depends on the symbols defined in `Kconfig` and on the implementation files `cn_queue.c`, `connector.c`, and `cn_proc.c`.

## Risks And Edge Cases
Adding new connector core sources requires updating `cn-y`. Building `cn_proc.o` separately means initialization ordering depends on connector core init being available for `cn_add_callback()`.

## Test Signals
Build tests should verify that `cn.o` contains both queue and transport code, that `cn_proc.o` appears only with `CONFIG_PROC_EVENTS`, and that module/built-in combinations match Kconfig constraints.
