# sources/distributed-fs/ceph-client/include/dt-bindings/clock/xlnx-vcu.h

## Purpose
Defines clock indexes for the Xilinx VCU binding. The IDs describe encoder and decoder core/MCU clocks exposed by the VCU clock provider.

## Important APIs, Types, and Constants
Exports `CLK_XVCU_ENC_CORE`, `CLK_XVCU_ENC_MCU`, `CLK_XVCU_DEC_CORE`, `CLK_XVCU_DEC_MCU`, and `CLK_XVCU_NUM_CLOCKS`. The final macro gives the provider/consumer count of clocks.

## Control Flow and State
No runtime flow or local state. The VCU driver interprets these indexes when acquiring clocks.

## Dependencies and Integration Points
Self-contained DT binding included by Xilinx ZynqMP/VCU DTS nodes and VCU driver code.

## Risks and Test Signals
The count macro should track the highest valid index plus one. Test signals include DT schema validation and media encode/decode probe tests that acquire all four clocks.
