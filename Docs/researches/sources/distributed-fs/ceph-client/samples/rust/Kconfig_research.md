# sources/distributed-fs/ceph-client/samples/rust/Kconfig

## Purpose

This Kconfig file defines the top-level Rust samples menu and individual build options for Rust kernel sample modules and host programs.

## Important APIs, Types, and Functions

It uses `menuconfig SAMPLES_RUST`, gated by `depends on RUST`, then declares tristate sample symbols such as `SAMPLE_RUST_CONFIGFS`, `SAMPLE_RUST_MISC_DEVICE`, `SAMPLE_RUST_DMA`, bus driver samples, and `SAMPLE_RUST_HOSTPROGS`. Some entries express dependencies or selects, including `CONFIGFS_FS`, `DEBUG_FS`, `I2C=y`, `PCI`, `USB=y`, `AUXILIARY_BUS`, and `SOC_BUS`.

## Control Flow

Kconfig exposes child options only inside `if SAMPLES_RUST`. Selected symbols drive `samples/rust/Makefile`, which maps configs to object files.

## State and Persistence Behavior

The file persists only kernel configuration choices in `.config`. Runtime state belongs to the compiled sample modules.

## Dependencies and Integration Points

It integrates with the kernel Rust build infrastructure, Kbuild objects in this directory, and subsystem Kconfig symbols for configfs, debugfs, PCI, I2C, USB, auxiliary bus, and SoC bus.

## Risks and Edge Cases

Dependencies such as `I2C=y` and `USB = y` intentionally require built-in core support; module-only subsystem configurations may hide samples. Missing or renamed source files will surface in Kbuild.

## Test Signals

Run menuconfig or `scripts/config` to enable samples, build `samples/rust`, and confirm expected `.o` or `.ko` artifacts are produced.
