# sources/distributed-fs/lizardfs/src/protocol/tstoma.h

Purpose: Defines tapeserver-to-master packets for tapeserver registration and reporting available tape files.

Important APIs/types/functions: `tstoma::registerTapeserver` with version and name; `tstoma::hasFiles` with `std::vector<TapeKey>`; `tstoma::endOfFiles`.

Control flow: Macro-generated serialization emits registration, file-list batches, and an empty end marker. Master-side handlers use these to build tape availability state.

State and persistence: Stateless wire definitions. Payloads describe tapeserver identity and tape contents.

Dependencies and integration: Depends on `common/tape_key.h`, packet helpers, and serialization macros. Pairs with `matots.h` master-to-tapeserver responses.

Risks and test signals: No direct tests. Risks include unbounded vector payloads if callers do not cap batches and compatibility around `TapeKey` serialization.
