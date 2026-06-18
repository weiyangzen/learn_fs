# sources/distributed-fs/ceph-client/arch/csky/boot/dts/Makefile

## Purpose

declares C-SKY devicetree build participation for board dtb files

## Important APIs, Types, and Functions

Source read size: 2 lines, 106 bytes. Build selections: `dtb-y -> $(patsubst $(src)/%.dts,%.dtb,
$(wildcard $(src)/*.dts))`.

## Control Flow and Behavior

the Makefile is intentionally minimal and lets parent boot rules discover dtb targets

## State and Persistence

there is no runtime state in the file

## Dependencies and Integration Points

integrates with arch/csky/boot/Makefile and generic dtbs targets

## Risks and Test Signals

missing dtb entries prevent board image generation; dtbs target builds are the signal
