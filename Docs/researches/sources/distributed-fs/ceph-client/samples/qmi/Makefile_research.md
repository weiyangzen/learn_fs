# sources/distributed-fs/ceph-client/samples/qmi/Makefile

## Purpose

This Kbuild fragment builds the QMI sample client module when `CONFIG_SAMPLE_QMI_CLIENT` is enabled.

## Important APIs, Types, and Functions

It uses the standard `obj-$(CONFIG_...) += object.o` Kbuild pattern and maps `qmi_sample_client.c` to `qmi_sample_client.o`.

## Control Flow

There is no runtime control flow. During kernel build, Kbuild evaluates `CONFIG_SAMPLE_QMI_CLIENT`; `y` links the object built-in and `m` builds a module.

## State and Persistence Behavior

It does not persist runtime state. Its only effect is build graph inclusion.

## Dependencies and Integration Points

The symbol must be defined by surrounding Kconfig. The C file depends on QRTR/QMI, platform devices, and debugfs.

## Risks and Edge Cases

Build failures surface if QMI dependencies are not selected by Kconfig or if the object name and source file diverge.

## Test Signals

Enable the config, build `samples/qmi/`, and confirm `qmi_sample_client.o` or `.ko` is produced.
