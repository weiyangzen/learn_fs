# sources/distributed-fs/ceph-client/include/linux/soc/qcom/mdt_loader.h

Purpose: This header exposes Qualcomm MDT firmware loading helpers for remote processors and PAS/SCM-authenticated images.

Important APIs/types/functions: It defines MDT segment flags `QCOM_MDT_TYPE_MASK`, `QCOM_MDT_TYPE_HASH`, and `QCOM_MDT_RELOCATABLE`. APIs include `qcom_mdt_get_size`, `qcom_mdt_load`, `qcom_mdt_pas_load`, `qcom_mdt_load_no_init`, and `qcom_mdt_read_metadata`; disabled builds return `-ENODEV` or `ERR_PTR(-ENODEV)`.

Control flow: Remoteproc or subsystem drivers request firmware, calculate required memory, load segments into a memory region, optionally authenticate through PAS context, get relocation base, and read metadata for secure monitor calls.

State and persistence: Firmware contents are copied to reserved memory; relocation base and PAS context tie the image to remote-subsystem boot state.

Dependencies and integration: Uses firmware API, devices, physical addresses, and Qualcomm SCM PAS context. Integrates with remoteproc, modem/audio/GPU/DSP firmware loaders, and reserved memory.

Risks and test signals: Segment bounds, relocatable address handling, and metadata parsing are security-sensitive. Test malformed firmware, undersized memory regions, PAS load failure, no-init loading, and remoteproc boot/shutdown.
