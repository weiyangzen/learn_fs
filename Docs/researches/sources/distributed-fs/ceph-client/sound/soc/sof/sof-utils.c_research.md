# sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.c

Purpose: provides a generic SOF utility for building compressed firmware page tables from ALSA scatter-gather DMA buffers.

Important APIs/functions: `snd_sof_create_page_table()` computes the number of aligned pages with `snd_sgbuf_aligned_pages()`, retrieves each page frame number with `snd_sgbuf_get_addr() >> PAGE_SHIFT`, and packs 20-bit PFN chunks into a compact little-endian byte table, where two PFNs occupy five bytes. It returns the page count and exports the symbol.

Control flow/state: the function is stateless and writes only the caller-supplied `page_table` buffer. Odd/even pages share bytes; odd entries preserve the low nibble already written by the previous even entry.

Dependencies/integration: depends on ALSA memalloc scatter-gather helpers, unaligned little-endian stores, and the SOF firmware/IPC convention for compressed page tables. It is used by stream or firmware paths that need DSP-readable DMA page lists.

Risks/test signals: callers must provide a large enough page table buffer; the function does not validate `size` against `page_table` capacity. Tests should cover one, two, and odd page counts, high PFNs, SG buffers crossing page boundaries, and byte-for-byte expected packing.
