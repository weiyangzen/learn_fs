# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_3_regs.h

Purpose: auto-generated Goya register-address map for DMA channel 3, an instance of the `DMA_CH` prototype. It exposes the memory-mapped offsets used to program direct linear DMA and tensor DMA transfers on the fourth DMA channel.

Important APIs/types/functions: no C functions or types are declared. The public interface is the `mmDMA_CH_3_*` macro family at the `0x419000` register window: channel configuration (`CFG0`, `CFG1`, `CFG2`), error/completion message address and data registers, LDMA source/destination/transfer-size/commit registers, status snapshots, read/write rate limit controls, TDMA source and destination base/ROI/size/valid-elements/start-offset/stride registers for five dimensions, and `MEM_INIT_BUSY`.

Control flow: this header has no executable flow. Driver code includes it through `goya_regs.h` and uses the constants as MMIO register identifiers when enabling, stopping, protecting, polling, or diagnosing DMA channel 3. The intended hardware sequence is configure addresses and transfer size, write `COMIT_TRANSFER`, then poll status/error/completion registers.

State and persistence: state lives in device registers, not in host memory. Programmed LDMA/TDMA descriptors, rate limit values, error-message targets, and status snapshots persist in the channel block until hardware reset or overwritten by the driver. `goya_blocks.h` maps the containing block as `mmDMA_CH_3_BASE` with a max offset of `0x200`.

Dependencies and integration: included by `goya_regs.h`; block-level base addresses come from `goya_blocks.h`. `goya_security.c` protects the channel 3 block with `goya_pb_set_block(hdev, mmDMA_CH_3_BASE)`, and `goya_coresight.c` references related DMA channel 3 CoreSight and bus-monitor bases from `goya_blocks.h`.

Risks: generated address drift is high impact because a wrong offset can start transfers from the wrong memory, corrupt destination memory, or hide channel errors. The macro name uses the generated spelling `COMIT_TRANSFER`, so manual code must match the header. TDMA has many repeated dimensional registers, making off-by-one or channel-3/channel-4 copy mistakes easy.

Test signals: compile coverage catches missing macros and include breakage. Runtime signals are successful DMA transfers through channel 3, valid completion messages, idle/status bits clearing after stop or reset, error-message delivery on invalid transactions, security-protection checks in `goya_security.c`, and CoreSight/bus-monitor visibility for DMA channel 3.
