# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_isadma.c

Purpose: Provides reusable ISA DMA allocation, programming, polling, and cleanup helpers for Comedi drivers that still use legacy ISA DMA channels.

Important APIs/types/functions: Exported APIs are `comedi_isadma_alloc()`, `comedi_isadma_free()`, `comedi_isadma_program()`, `comedi_isadma_disable()`, `comedi_isadma_disable_on_sample()`, `comedi_isadma_poll()`, and `comedi_isadma_set_mode()`. The code operates on `struct comedi_isadma` and `struct comedi_isadma_desc` from `comedi_isadma.h`.

Control flow: Allocation validates one or two descriptors, allocates a flexible `struct comedi_isadma`, selects a DMA-capable device (`dev->hw_dev` or a class device coerced to a 24-bit DMA mask), requests one or two ISA DMA channels, allocates coherent buffers for each descriptor, and initializes the DMA mode. `comedi_isadma_program()` claims the ISA DMA lock, clears the flip-flop, sets mode/address/count, and enables the channel. Disable stops the channel and returns residue. Disable-on-sample repeatedly re-enables short transfers until residue aligns with sample size or appears stalled. Poll reads residue, with special handling for `isa_dma_bridge_buggy`, and converts it to a byte position. Free releases coherent buffers and DMA channels.

State and persistence: State is the allocated DMA object, descriptor array, requested channels, coherent buffer virtual/bus addresses, max sizes, current DMA index, and direction mode. Hardware DMA controller state persists while a transfer is programmed; host objects are freed explicitly.

Dependencies and integration points: Depends on Linux ISA DMA APIs (`request_dma()`, `claim_dma_lock()`, `set_dma_*()`, `get_dma_residue()`), DMA mapping APIs, and Comedi device metadata. Parent drivers supply channel numbers, direction, and max buffer size, then use descriptors for device-specific transfers.

Risks: ISA DMA requires 24-bit addressable buffers and global DMA lock discipline. Residue reads can race hardware rollover; poll mitigates by reading twice. `comedi_isadma_disable_on_sample()` can spin briefly if hardware stalls mid-sample. Channel 0 is treated as no secondary channel in allocation/free logic, so callers must pass valid legacy DMA channels consistently. Test signals include allocation/failure cleanup, single and double-buffer channels, read/write mode setup, residue/poll behavior, sample-aligned disable, and parent hardware DMA transfer tests.
