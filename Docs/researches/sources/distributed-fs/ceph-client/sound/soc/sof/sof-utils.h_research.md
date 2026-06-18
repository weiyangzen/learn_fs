# sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.h

Purpose: declares the SOF utility API for page table generation.

Important APIs/types: forward declares `struct snd_dma_buffer` and `struct device`, and declares `snd_sof_create_page_table()`.

Control flow/state: no state; consumers pass all buffers and sizes explicitly.

Dependencies/integration: included by code that needs SOF compressed page-table creation without pulling the full private SOF header. It relies on ALSA DMA buffer types supplied by including compilation units.

Risks/test signals: signature changes affect stream/page-table callers. Build tests should ensure users include the right ALSA headers for full type definitions before calling the function.
