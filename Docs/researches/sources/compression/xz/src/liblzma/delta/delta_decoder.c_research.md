# sources/compression/xz/src/liblzma/delta/delta_decoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.c -->
## sources/compression/xz/src/liblzma/delta/delta_decoder.c

### Purpose
`delta_decoder.c` implements the Delta filter decoder and Delta property decoding.

### Important APIs, Types, And Functions
`decode_buffer()` reverses byte Delta in-place. `delta_decode()` runs the next coder, then decodes the newly produced output range. `lzma_delta_decoder_init()` installs the decode callback and calls common initialization. `lzma_delta_props_decode()` parses the one-byte distance property into `lzma_options_delta`.

### Control Flow
The decoder calls the next filter first, tracking the output start offset. It then adds the historical byte at `distance + pos` modulo 256 to each new byte and stores the decoded byte back into history. Property decoding requires exactly one byte and maps stored distance `0..255` to liblzma distance `1..256`.

### State, Persistence, And Dependencies
State is the shared Delta history ring in `lzma_delta_coder`. The file depends on `delta_private.h`, chained filter callbacks, and allocator helpers.

### Integration Points
Raw and Block decoder chains use this when a Delta filter appears before an LZMA/LZMA2 filter. The property decoder is used while parsing filter flags.

### Risks
The decoder assumes `coder->next.code` is present; Delta decode is modeled as postprocessing another filter's output in this path. The modulo-256 history ring depends on `pos-- & 0xFF` behavior.

### Test Signals
Round-trip tests for all distances, chunked output buffers, chained decode after LZMA2, property-size rejection, and NULL/zero-size output behavior are relevant.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.c -->
