# sources/distributed-fs/coda/coda-src/venus/local_vol.cc

Purpose: provides small local-repair helpers on `reintvol` for abort accounting, unrepaired-CML detection, and repair transaction id generation.

Important APIs and flow: `IncAbort` increments CML abort state for a tid and clears `CML.owner` when the log becomes empty. `ContainUnrepairedCML` walks the CML in commit order and returns true if any entry is marked `IsToBeRepaired`. `GetReintId` increments the recoverable `reint_id_gen` and returns the new id.

State and persistence: CML abort state and owner live in the volume's modify log; `reint_id_gen` is recoverable and updated under an RVM transaction. The unrepaired scan is read-only.

Dependencies and integration: depends on `ClientModifyLog`, `cml_iterator`, `cmlent::IsToBeRepaired`, recovery macros, and `venusvol` reint volume state.

Risks and test signals: risks are owner clearing when abort removes the last entry, transaction id wraparound/uniqueness over restart, and scans racing with log mutation in cooperative scheduling. Tests should cover abort of last and non-last entries, unrepaired CML detection, and persistent monotonic ids.
