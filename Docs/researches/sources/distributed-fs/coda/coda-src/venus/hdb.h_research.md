# sources/distributed-fs/coda/coda-src/venus/hdb.h

Purpose: declares the hoard database public pioctl messages, daemon request enum, persistent `hdb`/`hdbent` classes, transient `namectxt` path-expansion model, iterators, constants, and helper macros.

Important APIs and types: external message structs describe add/delete/clear/list/walk/verify commands. Hoard priorities range from `H_MIN_PRI` to `H_MAX_PRI`, and attributes `H_INHERIT`, `H_CHILDREN`, and `H_DESCENDENTS` control directory meta-expansion. `hdb` owns the recoverable hash table, freelist, transient priority queue, advice counters, and command methods. `hdbent` stores key, uid, priority, expansion flags, and one root `namectxt`. `namectxt` stores root directory fid, path, uid, priority, state, in-use/death/demote flags, expansion bindings, child meta-expansions, version state of expanded directories, parent/child links, and priority-queue/free-list handles. `hdb_iterator` filters by uid or key.

State and persistence: the header explicitly separates recoverable members from transient members with comments. `hdb` and `hdbent` are RVM-managed; `namectxt` instances are VM-only and rebuilt in `ResetTransient`.

Dependencies and integration: depends on Coda/Vice types, util containers (`rec_ohash`, `rec_olist`, `bstree`, `dlist`), FSDB/fsobj declarations, recovery annotations, daemon entry points, and `struct uarea` for request authorization context.

Risks and test signals: risks are ABI drift for pioctl message structs, invalid state transitions not caught until `CHOKE`, memory-ownership confusion for `namectxt::path` because root contexts borrow `hdbent::name` while meta contexts allocate, and mismatch between persistent and transient initialization. Tests should compile both Venus and hoard-tool users, exercise restart reconstruction, verify priority ordering, and validate `PRINT_*` macros for diagnostics.
