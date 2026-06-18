## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.hh

Purpose: declares the staged fluent URL builder interfaces.

Important APIs/types/functions: interfaces `URLBuilderProtocol`, `URLBuilderHostname`, `URLBuilderPort`; concrete `URLBuilder` implements them and exposes `build`, `add`, and static `getInstance`.

Control flow: private constructor plus staged return types guide callers through protocol -> hostname -> port -> path additions.

State and persistence: mutable URL string inside builder.

Dependencies and integration points: consumed by tape handler discovery URL generation.

Risks and test signals: inheritance is private for `URLBuilderHostname` and `URLBuilderPort`, relying on member function return types; compile tests should cover intended chained calls.
