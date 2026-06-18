# File Research: sources/block-storage/lvm2/libdm/misc/kdev_t.h

## Summary
Defines Linux kernel-style `dev_t` major/minor encoding and decoding macros for libdm.

## Main Contents
- `MAJOR(dev)`
- `MINOR(dev)`
- `MKDEV(ma, mi)`

## Important Behavior
The macros implement the split Linux device-number layout where major occupies bits derived from `0xfff00`, and minor combines low 8 bits with high minor bits shifted from bit 12.

## State and Lifetime
Pure preprocessor helper header with no runtime state.

## Risks
These macros intentionally shadow common system macros and assume Linux-style `dev_t` layout. Including order matters where system headers also define `major`, `minor`, or related helpers.
