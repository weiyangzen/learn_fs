## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_rtr_regs.h

Purpose: auto-generated TPC4 router register map. It defines 150 `mmTPC4_RTR_*` offsets from `0xF00100` through `0xF00604`, matching the `TPC_RTR` layout and TPC4 router base.

Important API surface: HBW/LBW read-request, read-response, write-request, write-response arbiters for five directions; per-direction max registers; debug arbiter controls; split coefficient table and split read/write rate controls; HBW 64-bit range mask/base pairs; LBW 16-entry range mask/base tables; regulator command/result registers; scrambling controls.

Control flow and state: no C control flow. The registers parameterize router arbitration and address-range steering for TPC4 traffic. Values persist in hardware until reset or reconfiguration.

Dependencies and integration: included through `goya_regs.h`; block base and max offset are declared in `goya_blocks.h`; security and debug/coresight code interact with surrounding TPC router/funnel regions.

Risks and test signals: range-mask errors can expose or misroute memory; arbitration errors can cause throughput collapse or timeouts. Test with TPC4 memory access patterns, HBW/LBW routing coverage, error interrupt checks, and validation against generated hardware XML/spec output.
