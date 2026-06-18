# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/Makefile

## Purpose
Builds the VirtualBox guest integration module.

## APIs, Types, and Functions
Defines `vboxguest-y` as `vboxguest_linux.o`, `vboxguest_core.o`, and `vboxguest_utils.o`, then maps `CONFIG_VBOXGUEST` to `vboxguest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
The object list combines Linux device glue, core protocol logic, and utility helpers into one module used by VirtualBox guest integration.

## Risks and Test Signals
Build-test module and built-in variants, with attention to object ordering if initialization dependencies change.
