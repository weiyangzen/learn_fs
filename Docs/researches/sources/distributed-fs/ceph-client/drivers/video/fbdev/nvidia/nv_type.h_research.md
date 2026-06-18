# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_type.h

## Purpose

`nv_type.h` defines the shared data structures, architecture constants, and bitfield helpers for the NVIDIA fbdev driver. It is the state contract used by all `nvidiafb` implementation files. The source was read as a complete 176-line file.

## Important APIs, Types, and Functions

Important macros are `NV_ARCH_04`, `NV_ARCH_10`, `NV_ARCH_20`, `NV_ARCH_30`, `NV_ARCH_40`, `BITMASK`, `MASKEXPAND`, `SetBF`, `GetBF`, `SetBitField`, `SetBit`, `Set8Bits`, and `V_DBLSCAN`. Types include `NVFBLayout`, `struct nvidia_i2c_chan`, `RIVA_HW_STATE`, `struct riva_regs`, and `struct nvidia_par`. `RIVA_HW_STATE` contains VGA arrays plus NVIDIA extended mode registers. `struct nvidia_par` contains saved/current state, PCI device, framebuffer/MMIO addresses, architecture/chipset, panel/head flags, DMA state, cursor and acceleration fields, I2C channels, and register-bank pointers.

## Control Flow

There is no executable flow. The structs are allocated as `fb_info->par` in `nvidiafb_probe()` and are read/written by setup, mode-setting, acceleration, backlight, I2C, and remove paths.

## State and Persistence Behavior

This header defines the in-memory persistent state for a bound NVIDIA fbdev device. `SavedReg`, `ModeReg`, and `initial_state` preserve hardware state for suspend/open/release/mode-set transitions. Address fields and register pointers persist from probe until remove. DMA fields persist across accelerated operations and are reset on mode set. Nothing is persisted beyond driver lifetime.

## Dependencies and Integration Points

The header includes fbdev, Linux types, I2C bit-bang types, and VGA helpers. Every NVIDIA fbdev source includes it directly or indirectly, making it the central ABI between files.

## Risks and Edge Cases

Structure layout changes can affect assumptions across the driver but not user ABI. Bitfield helper macros use unusual `high:low` macro arguments and depend on integer widths; misuse can silently program wrong register bits. The large `struct nvidia_par` mixes ownership for many subsystems, so cleanup must match which fields were initialized on each error path.

## Test Signals

Build coverage is the primary direct signal. Runtime signals include correct cleanup after partial probe failures, suspend/resume preserving `SavedReg`, mode-set updating `ModeReg`/`CurrentState`, and accelerated operations mutating DMA fields without corrupting unrelated state.
