# sources/distributed-fs/coda/coda-src/auth2/Makefile.am

Purpose: Automake recipe for Coda auth2 client tools, server daemon, generated RPC2 stubs, and auth helper libraries.

Important APIs/build targets: Builds `libauser.la` always, client programs `au`, `clog`, `cpasswd`, `ctokens`, `cunlog` when `BUILD_CLIENT`, and server pieces `libauth2.la`, `auth2`, `initpw`, `tokentool` when `BUILD_SERVER`. Includes `auth2.rpc2` via shared RPC2 rules.

Control flow: Declares generated client/server/helper RPC2 sources as nodist library sources. Sets include paths for RPC2, base, kerndep, util, and `coda-src/al`. Configures distinct `LDADD` sets for user tools, auth2 server, token tool, and initpw.

State and persistence: Build metadata only.

Dependencies and integration: Links client auth against `libauser`, util, kerndep, base, and RPC2. Links server auth against `libauth2`, AL, util, rwcdb, base, and RPC2.

Risks and test signals: Conditional targets mean auth code coverage depends on client/server build flags. Duplicate `au` appears in `bin_PROGRAMS`, which may be harmless or an automake warning depending on tooling.
