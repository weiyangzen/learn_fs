# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingValidator.java

Purpose: validates decode outputs by using the same decoder to reconstruct one originally valid input from the produced outputs and remaining inputs, then comparing buffers.

Important APIs/types/functions: constructor with `RawErasureDecoder`; `validate(ByteBuffer[], int[], ByteBuffer[])`; `validate(ECChunk[], ...)`; buffer allocation/reset helpers; `getNewValidIndexes()` and `getNewErasedIndex()` visible for tests.

Control flow: it marks output buffers, chooses the first valid input as a shape template, allocates/reuses a validation buffer matching directness and at least remaining capacity, builds new inputs by substituting decoded outputs into erased positions, selects one original input as the new erased target, decodes into the validation buffer, then compares the reconstructed bytes with the original input. Finally it advances original inputs to limits and resets outputs to their marks.

State and persistence: holds reusable validation `ByteBuffer` plus last validation indexes for testing. No durable persistence.

Dependencies and integration: uses `CoderUtil`, `ECChunk`, `RawErasureDecoder`, and `InvalidDecodingException`.

Risks: recursively invokes the decoder, so decoder state/caching bugs can affect validation; caller must pass input positions at readable starts. Tests should cover successful validation, forced corrupted output, direct and heap buffers, position restoration of outputs, input advancement, and new valid-index selection.
