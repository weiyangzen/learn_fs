# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/adsp_helper.h

Purpose: Defines shared MediaTek ADSP private data carried by SOF platform drivers and common IPC helpers.

Important types: `struct mtk_adsp_chip_info` stores physical/virtual SRAM, DRAM, config, secure, and bus register mappings, sizes, boot address, and AP/DSP DRAM offset. `struct adsp_priv` stores the owning device, `snd_sof_dev`, MediaTek IPC handle, child IPC platform device, chip info, clock array, optional address conversion callbacks, and private extension data.

Control flow and integration: MT8186 and MT8195 probes allocate `adsp_priv`, attach it to `sdev->pdata->hw_pdata`, fill `mtk_adsp_chip_info` from device-tree resources/reserved memory, register `mtk-adsp-ipc`, and set IPC callback data through this structure. Clock helpers store `struct clk **clk` here.

State and persistence: Lifetime is devm-managed by the platform device except for the child IPC platform device, which remove paths unregister explicitly. The register and memory mappings persist for the SOF device lifetime.

Risks: Both SoC drivers assume `hw_pdata` points to a valid `adsp_priv` before clock/common helpers run. Address conversion callbacks are declared but not populated by these files, so future users must check null. Resource fields differ by SoC; common code must not assume secure/bus registers always exist.

Test signals: Probe allocation failures, absent resources, child IPC registration/defer, clock helper access before initialization, and remove path with partially initialized private data.
