<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/fw.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/fw.h

Purpose: defines the SOF firmware container file format: global header, module headers, block headers, block target memory types, and firmware signature/header ABI.

Important APIs and types: `snd_sof_fw_header` holds `"Reef"`, file size, module count, and header ABI. `snd_sof_mod_hdr` describes base firmware or loadable module sections and block count. `snd_sof_blk_hdr` describes individual IRAM/DRAM/SRAM/ROM/IMR/reserved blocks by type, payload size, and target offset. All layout structs are packed.

Control flow: the SOF driver validates the file signature/header ABI, iterates modules, then iterates blocks and copies each block payload to the memory area implied by the type and offset before starting firmware.

State and persistence: this describes persistent firmware image bytes on disk. Runtime state arises after the loader places blocks into DSP/host memory.

Dependencies and integration points: depends on Linux types and integrates with firmware_class loading, SOF platform loaders, DSP memory maps, and firmware build tools.

Risks and test signals: risks include trusting file/module/block sizes, integer overflow while walking packed blobs, negative enum values in packed ABI, and target offset validation. Test malformed firmware headers, truncated modules, unknown block types, multiple modules, and loader bounds on each target memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/fw.h -->
