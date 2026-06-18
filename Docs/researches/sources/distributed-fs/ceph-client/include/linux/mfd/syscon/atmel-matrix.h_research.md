# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-matrix.h

## Purpose

This 112-line header defines Atmel AT91/SAMA5 MATRIX memory-controller system peripheral register offsets and bitfields.

## Important APIs, Types, and Functions

It exports variant-specific matrix register offsets, helper macros for master/slave configuration, ULBT, default master, arbitration, ITCM/DTCM sizing, priority registers, remap control, chip-select assignment, voltage IO selection, EBI/DDR IO settings, NAND selection, DDR multi-port enable, and USB pull-up control.

## Control Flow

No executable flow. SoC drivers use syscon regmaps and these macros to configure bus arbitration, remap behavior, EBI/DDR/NAND options, and USB pull-up routing.

## State and Persistence Behavior

State persists in system controller registers and affects memory bus topology, boot/remap behavior, chip-select routing, and IO voltage configuration.

## Dependencies and Integration Points

It integrates Atmel syscon consumers such as memory controller, NAND, USB, board init, and bus arbitration drivers.

## Risks and Edge Cases

Offsets vary by SoC; using the wrong variant offset can change unrelated system registers. IO voltage and chip-select settings are board-critical.

## Test Signals

Build tests for AT91/SAMA5 users, register offset validation per compatible, masked update tests, and boot/hardware tests for EBI/NAND/USB configuration.
