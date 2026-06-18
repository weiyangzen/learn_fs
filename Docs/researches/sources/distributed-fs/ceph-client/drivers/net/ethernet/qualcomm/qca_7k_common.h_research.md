<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.h

## Purpose
`qca_7k_common.h` defines the shared QCA7K Ethernet-over-serial framing protocol contract for SPI and UART drivers.

## Important APIs, Types, and Data
- Error/status constants include `QCAFRM_GATHER`, `QCAFRM_NOHEAD`, `QCAFRM_NOTAIL`, `QCAFRM_INVLEN`, and `QCAFRM_INVFRAME`.
- MTU/frame constants define Ethernet min/max MTU, min/max frame lengths, header length, and footer length.
- `enum qcafrm_state` encodes SPI hardware-length states, header-byte states, length/reserved states, payload countdown, and footer states.
- `struct qcafrm_handle` stores current state, initial state, and an offset/temporary length.
- Inline initializers choose SPI or UART initial states.
- Declares header/footer creation and FSM decode functions.

## Control Flow
The header has inline initialization flow only: SPI starts at `QCAFRM_HW_LEN0`; UART starts at `QCAFRM_WAIT_AA1`.

## State and Persistence
`struct qcafrm_handle` is per receiver and persists across serial callbacks or SPI burst reads. Its `offset` field doubles as temporary length storage during header parsing.

## Dependencies and Integration Points
Includes Ethernet/VLAN headers and is consumed by QCA SPI and UART netdev drivers plus the common implementation.

## Risks and Edge Cases
State enum values intentionally count downward through negative values and then positive payload lengths; changing them can break decode logic. Buffer-size and MTU constants must remain consistent with both transports' skb allocation.

## Test Signals
Build and transport tests should verify both `qcafrm_fsm_init_spi()` and `qcafrm_fsm_init_uart()` produce decodable streams for their respective hardware framing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.h -->
