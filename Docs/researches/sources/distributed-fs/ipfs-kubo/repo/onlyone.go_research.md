# sources/distributed-fs/ipfs-kubo/repo/onlyone.go

Purpose: ensures a repo keyed by an arbitrary comparable value is opened only once per process and shared through reference-counted wrappers.

Important APIs and control flow: `OnlyOne.Open` initializes the active map, returns an existing `ref` when present or calls the provided open function and stores a new `ref`. It increments `refs` under a mutex. `ref.Close` decrements refs, returns without closing while refs remain, and on the final close removes the entry and closes the underlying repo.

State and persistence: in-memory active map only; underlying repo controls disk persistence and locks.

Dependencies and integration: used by `fsrepo.Open` and `OpenWithUserConfig` to avoid duplicate same-process opens against the same repo path.

Risks and test signals: key must be comparable or map access panics; keys should avoid collisions across repo implementations. If a caller forgets to close, the repo remains active. fsrepo tests cover same-process double open and reference close behavior.
