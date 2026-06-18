# sources/distributed-fs/ceph-client/include/linux/ppp-comp.h

Purpose: declares the PPP compression plugin interface used by compressor modules and generic PPP CCP handling.

Important APIs and types: `struct compressor` defines protocol number, compressor/decompressor allocation/free/init/reset callbacks, packet compress/decompress functions, incompressible-packet update hook, stats hooks, module owner, and extra skb space. Constants enable BSD-Compress and Deflate by default, disable Predictor variants, and define decompression error codes `DECOMP_ERROR` and `DECOMP_FATALERROR`. APIs register/unregister compressor implementations.

Control flow: a compressor module registers its callback table, PPP negotiates CCP options, allocates TX/RX compressor state, initializes it with options/unit/debug data, compresses outgoing packets, decompresses incoming packets, updates state on incompressible packets, reports stats, and unregisters on module removal.

State and persistence: per-link compressor state is allocated by callbacks and owned by PPP until freed. Module owner protects implementation lifetime; no persistent state is held in the header.

Dependencies and integration points: depends on PPP compression UAPI, PPP generic layer, sk_buff sizing, module refcounts, and compression algorithm modules.

Risks and test signals: risks include module unregister while state is active, buffer-size/extra-headroom mistakes, decompression fatal vs recoverable error confusion, option parsing bugs, and patent-related CCP reset behavior around fatal errors. Test compressor registration, CCP negotiation, compress/decompress round trips, incompressible updates, stats, error returns, MTU/MRU limits, and module unload with active PPP links.
