# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/xlnx-vcu.h

## Purpose

This 39-line header defines Xilinx VCU syscon register offsets for encoder/decoder enable, frame format, clocks, PLL, status, and gasket initialization.

## Important APIs, Types, and Functions

It exports register offsets such as `VCU_ECODER_ENABLE`, `VCU_DECODER_ENABLE`, memory depth, encoder/decoder color depth, range, frame size, color format, FPS, MCU/core/encoder/PLL/AXI clocks, video standards, status, core count, gasket init, and `VCU_GASKET_VALUE`.

## Control Flow

No executable flow. Xilinx media/clock drivers use these offsets through syscon/regmap to configure VCU encoder/decoder hardware and check status.

## State and Persistence Behavior

State persists in VCU control registers and describes active encoder/decoder configuration, clocking, PLL mode, buffer behavior, and gasket setup.

## Dependencies and Integration Points

It integrates Xilinx VCU syscon support with video codec drivers, clock configuration, and media pipeline setup.

## Risks and Edge Cases

The macro name `VCU_ECODER_ENABLE` appears misspelled but is ABI for users. Codec configuration fields must match firmware/hardware expectations for frame size, color, and clocks.

## Test Signals

Build tests for VCU consumers, register offset smoke tests, encoder/decoder bring-up tests, and media pipeline format/clock validation.
