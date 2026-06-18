# File Research: sources/block-storage/lvm2/lib/device/dev-dasd.c

## Purpose
Detects whether an IBM s390 DASD device is CDL formatted.

## Core Behavior
On Linux, the file defines the needed DASD userspace ioctl structures and constants locally, opens the device read-only, calls `BIODASDINFO2`, and checks whether `format == DASD_FORMAT_CDL`.

On non-Linux builds, `dasd_is_cdl_formatted()` always returns 0.

## Integration
Used by device-type probing code for platform-specific DASD handling.

## Risk Notes
The function depends on a Linux DASD ioctl ABI copied into this file. It opens and closes the device itself, so failures in open, ioctl, or close are logged and reported as not CDL-formatted.
