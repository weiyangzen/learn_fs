# sources/distributed-fs/lizardfs/src/protocol/matots.h

Purpose: Defines master-to-tapeserver packets for tapeserver registration responses and tape file placement instructions.

Important APIs/types/functions: `matots::registerTapeserver` status and response packet versions; `matots::putFiles` carrying `std::vector<TapeKey>`.

Control flow: Registration can return a status-only failure or a response containing master version. `putFiles` sends a vector of tape keys for files that the tapeserver should place/store.

State and persistence: Stateless serialization; it conveys tape archive work and registration state but does not manage tape state itself.

Dependencies and integration: Uses packet serialization macros and `TapeKey` through included common headers. It integrates with tapeserver/master tape-copy coordination.

Risks and test signals: Main risks are missing direct tests and vector size/format compatibility for tape contents. Consumers must inspect packet version before decoding registration responses.
