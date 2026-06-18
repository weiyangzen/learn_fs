# sources/distributed-fs/eos/mgm/lru/LRU.hh

Purpose: declares the MGM LRU engine, policy parser data structures, public controls, and the private background scan interface. It is the contract used by MGM configuration/admin code and by unit tests for parser behavior.

Important APIs and types: `LRU::Options` carries `enabled` and scan `interval`. `PolicyRule` captures a filename regex, required age, optional signed size condition, and fixed `now` timestamp; it provides `nameMatches`, `ageMatches`, `sizeMatches`, `getSizeCriteria`, and `matches`. `PolicyRules` is a vector of rules. Static parser helpers are `extractTimeSizeCriterias`, `parseExpireMatchPolicy`, and `parseExpireSizeMatchPolicy`. Public methods include `getOptions`, `getLRUIntervalConfig`, `Start`, `Stop`, `AgeExpireEmpty`, `SizeAgeExpire`, `CacheExpire`, `ConvertMatch`, and `RefreshOptions`. `lru_entry_t` is a sortable path/ctime/size tuple for watermark expiry.

Control flow and state model: callers construct `LRU`, call `Start`, and can request option reload by setting `mRefresh` through `RefreshOptions`. The private background path is `backgroundThread`, which calls `performCycleQDB`; every discovered directory is passed to `processDirectory`. `PolicyRule` freezes `m_now` at parse time so every file in one policy application uses a consistent age cutoff.

State and persistence behavior: the header stores only runtime scanning state: `mQcl`, `mThread`, root virtual identity, XRootD error info, and an atomic refresh flag. Persistent behavior is indirect through namespace xattrs and file deletion/conversion effects.

Dependencies and integration points: includes assisted threads, mapping, regex wrapper, namespace interfaces, XRootD error info, `qclient::QClient`, and EOS virtual identity. `gLRUPolicyPrefix` names the policy xattr wildcard used by namespace scanning/configuration.

Risks and test signals: `PolicyRule::sizeMatches` treats positive sizes as `fileSize > limit` and negative sizes as `fileSize < limit`; callers expecting inclusive comparisons should test boundary files. `nameMatches("*")` is a special compatibility case outside the regex wrapper. Unit tests already cover parser helpers and equality; additional tests should cover `PolicyRule::matches` against boundary ctime and size values and `RefreshOptions` interaction with the running thread.
