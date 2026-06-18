# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/defines.h

## Purpose
`defines.h` centralizes `igbvf` hardware constants: descriptor alignment, RX/TX descriptor status bits, device control/status fields, queue-enable bits, SRRCTL layout, DCA flags, speed/duplex values, and driver-local error codes.

## Important APIs, Types, And Functions
The file is macro-only. Key definitions include descriptor multiples (`REQ_TX_DESCRIPTOR_MULTIPLE`, `REQ_RX_DESCRIPTOR_MULTIPLE`), RX status and error masks (`E1000_RXD_STAT_*`, `E1000_RXDEXT_STATERR_*`), `E1000_RXDEXT_ERR_FRAME_ERR_MASK`, reset and link/speed bits (`E1000_CTRL_RST`, `E1000_STATUS_*`), advanced TX bits, maximum frame sizes, SRRCTL descriptor type and buffer size fields, queue enable bits, and `E1000_VF_INIT_TIMEOUT`.

## Control Flow
There is no direct control flow. These constants are consumed by `netdev.c`, `vf.c`, and the hardware register wrappers to encode register writes and decode descriptor writebacks.

## State And Persistence
No state is stored. The constants define how volatile hardware state is interpreted.

## Dependencies And Integration Points
The header is included by `vf.h`, which makes its constants available throughout the `igbvf` driver. It depends on common kernel bit macros such as `BIT()` through included headers in the includer chain.

## Risks
Incorrect constants can corrupt descriptor processing, interrupt programming, or reset behavior. The RX error mask controls packet drop decisions, so accidental changes can pass corrupted frames or drop valid traffic. Descriptor multiple values must remain compatible with hardware and ethtool ring resizing.

## Test Signals
Compile tests catch missing macros; functional tests should include RX checksum/error handling, jumbo MTU configuration, ethtool ring resizing alignment, queue enable/disable, and link speed reporting on VF hardware.
