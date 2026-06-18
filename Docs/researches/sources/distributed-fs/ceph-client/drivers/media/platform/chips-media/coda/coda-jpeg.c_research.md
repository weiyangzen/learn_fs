# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-jpeg.c

`coda-jpeg.c` implements JPEG support for both BIT JPEG paths and CODA960 direct JPEG hardware. It owns default Huffman/quantization tables, JPEG header parsing, quality scaling, hardware Huffman/quant table generation, direct JPEG encode/decode setup and finish, and the CODA960 JPEG IRQ.

Shared APIs are `coda_jpeg_write_tables()`, `coda_jpeg_check_buffer()`, `coda_jpeg_decode_header()`, and `coda_set_jpeg_compression_quality()`. Direct operation tables are `coda9_jpeg_encode_ops` and `coda9_jpeg_decode_ops`, with prepare/finish functions for encode and decode plus `coda9_jpeg_irq_handler()`.

Header parsing uses `v4l2_jpeg_parse_header()` and validates dimensions, three components, up to three 8-bit quantization tables, required Huffman tables, scan selectors, entropy-coded segment offset, and 4:2:0/4:2:2 subsampling. Direct encode writes a JPEG header into the capture buffer, configures BBC/GBU/GDI, loads Huffman and quantization tables, sets MCU info/restart interval/rotation, starts the JPEG engine, and computes payload from the BBC write pointer. Direct decode parses each frame, configures scaling, loads user/default tables, sets BBC/GBU from the entropy offset, writes destination addresses, and starts the engine.

JPEG state lives in `ctx->params` (`jpeg_qmat_tab`, indexes, Huffman selectors/tables/data, quality, restart interval, subsampling) plus `ctx->jpeg_ecs_offset`. The file depends on V4L2 JPEG helpers, vb2 dma-contig, CODA registers, GDI setup, `coda_write_base()`, and `coda_hw_reset()`.

Risks include narrow JPEG support, CPU mapping assumptions in marker checks, stride mismatch only logged on encode, busy loops with limited timeout coverage, and a suspicious mutex unlock in `coda9_jpeg_irq_handler()` when no current context exists. Test malformed headers, quality scaling, SOI/EOI validation, encode header validity, decode scaling, overflow timeout, error MB reporting, and repeated JPEG encode/decode context switches.
