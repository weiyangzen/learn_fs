# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_local.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_local.h` is the shared local input-system configuration type layer in the Intel AtomISP CSS driver. It defines CSI ports, network/control/channel/backend/switch config types, source config union, RX modes, compressor/predictor enums, and `rx_cfg_t`, then includes generation-specific local headers.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ctrl_unit_cfg_s`, `struct input_system_network_cfg_s`, `struct input_switch_cfg_channel_s`, `struct backend_channel_cfg_s`, `struct input_switch_cfg_s`, `struct rx_cfg_s`. Visible enums: `enum mipi_compressor`, `enum mipi_port_id		port;	/* The port ID to apply the control on */`. Important macros/constants: `UNCOMPRESSED_BITS_PER_PIXEL_10`, `UNCOMPRESSED_BITS_PER_PIXEL_12`, `COMPRESSED_BITS_PER_PIXEL_6`, `COMPRESSED_BITS_PER_PIXEL_7`, `COMPRESSED_BITS_PER_PIXEL_8`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Stream setup maps public stream input settings into these local configs before programming ISP2400/2401 input hardware.

## State and Persistence Behavior

State is caller-owned configuration passed to input-system setup code.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include invalid RX mode selection, using backward-compatible compression fields incorrectly, and mismatched two-PPC settings.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 142 lines, 3548 bytes.
