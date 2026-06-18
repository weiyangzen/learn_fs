# sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.h

Purpose: public header for the external sequence producer example.

Important APIs: includes `zstd.h` with `ZSTD_STATIC_LINKING_ONLY` and declares `simpleSequenceProducer()` using the zstd external sequence producer callback signature: producer state, output sequence buffer/capacity, source buffer/size, dictionary buffer/size, compression level, and window size.

State, dependencies, and integration: the header has no state. It is included by `main.c` and implemented by `sequence_producer.c`, binding the example to static-linking-only zstd sequence types.

Risks and test signals: include guard name `MATCHFINDER_H` is generic and could collide in larger integrations. Any signature drift in zstd's static sequence producer API will break this example at compile time, which the contrib build catches.
