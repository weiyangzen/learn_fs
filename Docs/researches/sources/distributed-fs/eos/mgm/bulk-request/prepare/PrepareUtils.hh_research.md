## sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.hh

Purpose: declares `PrepareUtils`, currently a stateless utility class for prepare option formatting.

Important API: `static std::string prepareOptsToString(int opts)`.

Integration: used by `PrepareManager::doPrepare()` logging. Risks are minimal, but because output is diagnostic, tests should focus on stability for common option combinations used in logs and troubleshooting.
