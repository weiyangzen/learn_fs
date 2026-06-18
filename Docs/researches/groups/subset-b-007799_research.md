# subset-b-007799 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_parse.c -->
## sources/distributed-fs/openafs/src/rxgen/rpc_parse.c

### Purpose
`rpc_parse.c` is the rxgen parser and procedure stub generator. It parses SunRPC/RXGEN IDL definitions, tracks package/opcode/stat metadata, and emits client stubs, server stubs, ubik callback wrappers, multi-call macros, opcode dispatch tables, and header statistics through shared `fout`.

### Important APIs, Types, And Functions
The public entry points are `get_definition()`, `er_Proc_CodeGeneration()`, `h_Proc_CodeGeneration()`, `h_opcode_stats()`, `generate_multi_macros()`, `IsRxgenToken()`, and `IsRxgenDefinition()`. Most work is in static helpers such as `def_struct`, `def_union`, `def_typedef`, `def_package`, `check_proc`, `analyze_ProcParams`, `cs_Proc_CodeGeneration`, `ss_Proc_CodeGeneration`, and opcode-dispatch emitters. It fills the AST types declared in `rpc_parse.h` and uses scanner tokens from `rpc_scan.c`.

### Control Flow
`get_definition()` reads the next token, dispatches to a definition parser, scans the terminating semicolon for ordinary RPCL definitions, and records definitions in global lists. Procedure parsing requires an active package, parses direction-tagged params, assigns or auto-increments opcodes, updates package/master opcode ranges, emits code immediately according to flags, records procedure metadata for later dispatch generation, and updates statistics arrays. Split and multi procedures temporarily hide IN or OUT params while emitting Start/End forms.

### State, Persistence, And Dependencies
The file is heavily stateful: package index, prefixes, opcode ranges, procedure lists, special typedef lists, function name arrays, stat indices, and split prefixes are globals reset by `reinitialize()` in `rpc_util.c`. Persistent output is generated C/header text written to `fout`. Dependencies include `rpc_scan` token routines, `rpc_util` allocation/error/list helpers, and `rpc_cout.c`/`rpc_hout.c` callbacks for XDR data and parameter-code generation.

### Integration Points
`rpc_main.c` drives this parser while selecting output modes with `Sflag`, `Cflag`, `hflag`, `cflag`, `uflag`, `xflag`, and related globals. Generated stubs integrate with Rx calls, XDR streams, rxgen error constants, ubik clients, rx statistics, and `rx_multi.h`.

### Risks
Fixed-size buffers and counters (`MAX_PACKAGES`, `MAX_FUNCTION_NAME_LEN`, function arrays, local 100/150/250-byte buffers) are central risk points. The parser interleaves parsing and code emission, so error recovery is impossible and global state ordering matters. Opcode auto-assignment forbids later explicit assignments, and old-style dispatch is selected when opcode holes exist. Memory is mostly process-lifetime allocation with limited frees because rxgen exits after generation.

### Test Signals
Useful tests include IDL fixtures for structs, unions, typedef aliases, variable arrays, strings, packages, explicit and implicit opcodes, opcode holes, split and multi procedures, ubik output, custom/special declarations, stats output, and boundary failures for long function names or too many packages/functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_parse.h -->
## sources/distributed-fs/openafs/src/rxgen/rpc_parse.h

### Purpose
`rpc_parse.h` defines the in-memory AST and procedure metadata used by rxgen parsing and generation.

### Important APIs, Types, And Functions
Core enums are `defkind` for definition/procedure component kinds and `relation` for alias, pointer, fixed vector, and variable array declarations. Important structures include `declaration`, `decl_list`, `enumval_list`, `case_list`, `typedef_def`, `struct_def`, `union_def`, `param_list`, `proc1_list`, `procedure_def`, `special_def`, `spec_list`, and top-level `definition`.

### Control Flow
The header has no executable flow, but its layout drives parser and generator decisions. `definition.def_kind` selects the active union member, while `definition.pc` is populated for procedures. `param_list.param_kind`, `param_flag`, and `procedure_def.paramtypes[IN/OUT/INOUT]` control marshal/unmarshal generation.

### State, Persistence, And Dependencies
Instances are allocated by parser helpers and stored in global `rxgen_list` chains. Procedure and declaration strings are scanner-owned heap allocations or string literals. The header assumes `char` flag fields can hold bitwise param flags such as `FREETHIS_PARAM` and `OUT_STRING`.

### Integration Points
`rpc_parse.c` creates these structures, `rpc_cout.c` and `rpc_hout.c` consume them for C/XDR/header output, and `rpc_util.c` inspects declarations for typedef/vector handling.

### Risks
The AST lacks ownership annotations, so freeing is intentionally minimal. `IN`, `OUT`, and `INOUT` macros are redefined in the header, which can surprise includers. Several fields are reused across definition kinds, so callers must honor `def_kind`.

### Test Signals
Compile coverage of every parser/generator object is the main signal. IDL tests should inspect generated output for correct relation handling, param flags, typedef expansion, and procedure direction counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_scan.c -->
## sources/distributed-fs/openafs/src/rxgen/rpc_scan.c

### Purpose
`rpc_scan.c` is rxgen's lexical scanner. It converts the input stream into `token` values, handles comments, preprocessor line directives, rxgen `%` passthrough directives, and verbatim `@{ ... @}` blocks.

### Important APIs, Types, And Functions
Public scanner routines are `scan`, `scan2`, `scan3`, `scan4`, `scan_num`, `peek`, `peekscan`, `get_token`, `unget_token`, `findkind`, and `printdirective`. Static helpers parse string constants and numeric constants, detect `#line`/preprocessor directives, and update logical source file/line information.

### Control Flow
`get_token()` first returns a pushed token if present. Otherwise it reads lines into global `curline`, advances `linenum`, skips whitespace and C comments, copies `%` directives to output without the leading percent, adjusts `infilename`/line number for preprocessor directives, and recognizes punctuation, strings, decimal/hex constants, identifiers, and reserved words.

### State, Persistence, And Dependencies
Global scanner state is `pushed`, `lasttok`, `scan_print`, and the `curline`/`where`/`linenum`/`infilename` globals defined in `rpc_util.c`. String and identifier token values are heap-allocated through `alloc`. Output directives persist as generated text in `fout`.

### Integration Points
The parser consumes tokens through the `scan*` helpers and relies on `expected*` functions in `rpc_util.c` for diagnostics. The symbol table includes rxgen extensions such as `package`, `prefix`, `statindex`, `startingopcode`, `splitprefix`, `multi`, and `afsUUID`.

### Risks
Only one-token pushback is supported. Comments and verbatim blocks are tracked locally inside `get_token()`, so unterminated multi-line constructs can create confusing behavior. Token buffers and line buffers are fixed size; strings are scanned only to the next quote without escape processing. Numeric constants with a leading `-` are scanned, but later validation accepts only decimal digits in some contexts.

### Test Signals
Scanner tests should cover every reserved word, illegal characters, string and hex constants, comments across lines, `%` passthrough output, preprocessor file/line changes, one-token pushback, verbatim blocks, and expected-token diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_scan.h -->
## sources/distributed-fs/openafs/src/rxgen/rpc_scan.h

### Purpose
`rpc_scan.h` declares the rxgen token kinds and the token carrier structure shared by the scanner, parser, and utility diagnostics.

### Important APIs, Types, And Functions
`enum tok_kind` covers identifiers, string constants, punctuation, standard RPCL keywords, rxgen extensions, direction markers, `afsUUID`, and EOF. `struct token` pairs a `tok_kind` with the token text pointer.

### Control Flow
There is no runtime flow; ordering must remain compatible with scanner symbol tables and diagnostic string tables in `rpc_scan.c` and `rpc_util.c`.

### State, Persistence, And Dependencies
Token text may point at static reserved-word strings or scanner-allocated memory. The header has no guard macro in this copy, so repeated inclusion relies on existing source include patterns.

### Integration Points
`rpc_parse.c` switches on these token kinds to build definitions, while `rpc_util.c` maps them back to display strings for `expected*` errors.

### Risks
Adding or reordering tokens requires synchronized updates to scanner recognition and diagnostic tables. Lack of an include guard can become a build issue if included indirectly more than once in a translation unit.

### Test Signals
Build tests plus scanner fixtures for all token kinds provide coverage. Any new token should have parser, scanner, and diagnostic coverage together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_util.c -->
## sources/distributed-fs/openafs/src/rxgen/rpc_util.c

### Purpose
`rpc_util.c` provides shared rxgen process state, list utilities, type-formatting helpers, diagnostics, cleanup-on-failure, and token expectation messages.

### Important APIs, Types, And Functions
Public functions include `reinitialize`, `streq`, `findval`, `storeval`, `fixtype`, `stringfix`, `ptype`, `isvectordef`, `pvname`, `error`, `crash`, `record_open`, `expected1` through `expected4`, and `tabify`. Static helpers implement typedef chasing, lowercasing, token-to-string mapping, and source caret printing.

### Control Flow
`reinitialize()` clears scanner buffers and parser globals before a generation run. `fixtype()` follows typedef aliases for vector element handling. `error()` prints the current source line and caret, reports filename and line, then calls `crash()`, which unlinks recorded output files and exits.

### State, Persistence, And Dependencies
The file owns `curline`, `where`, `linenum`, `infilename`, `outfiles`, `nfiles`, `fout`, `fin`, and `defined`. It mutates parser globals declared in `rpc_parse.c`. Output filenames recorded by `record_open()` persist only so failed generation can unlink partial files.

### Integration Points
All rxgen modules include these helpers via `rpc_util.h`. The scanner uses source-position globals and `expected*` diagnostics; the parser and emitters use type printing and definition lookup.

### Risks
The cleanup list is capped at six files. `error()` calls `crash()` twice, though the first exits. Fixed buffers for diagnostics and lowercased names can overflow if future token strings or names grow. `isvectordef()` is structured as an infinite loop with immediate returns and depends on valid `relation` values.

### Test Signals
Signals include parser error fixtures verifying caret placement and cleanup, typedef/vector formatting cases, repeated generation runs through `reinitialize()`, output-file count limits, and `scan_print` suppression behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_util.h -->
## sources/distributed-fs/openafs/src/rxgen/rpc_util.h

### Purpose
`rpc_util.h` is the shared rxgen internal header tying scanner, parser, main program flags, and output emitters together.

### Important APIs, Types, And Functions
It defines allocation and printing macros, `struct rxgen_list`, `MAXLINESIZE`, externs for command-line flags and global parser/scanner state, list macros `STOREVAL`/`FINDVAL`, and prototypes for scanner, parser, utility, C-output, and header-output functions.

### Control Flow
No code executes here, but macro behavior affects control flow: `f_print` emits only when `scan_print` is true, and `alloc`/`ALLOC` directly call `malloc` without checking.

### State, Persistence, And Dependencies
The header exposes many mutable globals, including package/opcode state and function name arrays. It includes `rxgen_consts.h` and depends on `definition`, `relation`, `proc1_list`, `tok_kind`, and `token` from parser/scanner headers.

### Integration Points
Every rxgen source uses this as the common internal contract. It also declares `rpc_main.c` flags that select client, server, header, combined, stats, ANSI, ubik, and opcode behaviors.

### Risks
Broad global exposure makes ordering bugs easy and unit isolation hard. Allocation macros hide unchecked malloc calls. `f_print` as a conditional statement macro can be fragile in nested `if/else` contexts if used without braces.

### Test Signals
Build all rxgen output modes and run IDL fixtures under both `scan_print` enabled and disabled. Static analysis should flag unchecked allocations and macro misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rxgen_consts.h -->
## sources/distributed-fs/openafs/src/rxgen/rxgen_consts.h

### Purpose
`rxgen_consts.h` centralizes rxgen generated-code return constants and compile-time bounds for packages and procedure names.

### Important APIs, Types, And Functions
It defines `RXGEN_SUCCESS`, client/server marshal and unmarshal errors, decode/opcode errors, XDR-free errors, call wait constants, `MAX_PACKAGES`, `MAX_FUNCTION_NAME_LEN`, `MAX_FUNCTIONS_PER_PACKAGE`, and `MAX_FUNCTIONS_PER_INTERFACE`.

### Control Flow
There is no runtime flow. Generated client/server stubs return these negative error codes when XDR operations fail or an unknown opcode is received.

### State, Persistence, And Dependencies
The header is guarded by `_RXGEN_CONSTS_` and has no mutable state. Its constants shape static arrays in `rpc_parse.c`.

### Integration Points
Included by `rpc_util.h`, generated stubs, and rxgk placeholder procedures. Runtime Rx code observes these values as procedure return errors.

### Risks
The numeric error values are arbitrary and must remain stable for generated-code compatibility. Increasing package/function limits changes static memory footprint and may reveal other fixed buffers.

### Test Signals
Generated stub tests should assert expected return codes for marshal/unmarshal/opcode failures and boundary tests should exercise package and function count limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rxgen_consts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/Makefile.in -->
## sources/distributed-fs/openafs/src/rxgk/Makefile.in

### Purpose
`rxgk/Makefile.in` builds and installs the rxgk security library, generated RPC stubs, generated error table, and public headers.

### Important APIs, Types, And Functions
Primary targets are `all`, `generated`, `depinstall`, `liboafs_rxgk.la`, `librxgk_pic.la`, `install`, `dest`, and `clean`. Generated artifacts come from `rxgk_int.xg` via `RXGEN` and `rxgk_errs.et` via `COMPILE_ET`.

### Control Flow
The default build installs headers into `TOP_INCDIR`, generates client/server/XDR/header files with `RXGEN -b -A -x`, compiles listed libtool objects, and links shared and PIC libraries against `opr`, `comerr`, `rx`, and RFC3961 crypto.

### State, Persistence, And Dependencies
Persistent outputs include generated `.cs.c`, `.ss.c`, `.xdr.c`, `rxgk_int.h`, `rxgk_errs.[ch]`, installed headers, and libtool libraries. Installation is conditional on `@ENABLE_RXGK@`.

### Integration Points
The makefile connects rxgk C sources to rxgen and comerr-generated protocol material. Public include users get `rxgk.h`, `rxgk_types.h`, `rxgk_errs.h`, and `rxgk_int.h`.

### Risks
`LT_libs` has a placeholder comment for future GSSAPI linkage, matching unimplemented GSS procedures. Clean removes generated RPC files but not every installed artifact. Conditional install means builds can produce libraries while packaging may skip headers if rxgk is disabled.

### Test Signals
Signals include clean-tree build, generated-file rebuild after `.xg` or `.et` changes, `ENABLE_RXGK` install/dest behavior, symbol export validation with `liboafs_rxgk.la.sym`, and dependency tracking for generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk.h -->
## sources/distributed-fs/openafs/src/rxgk/rxgk.h

### Purpose
`rxgk.h` is the public rxgk API header for creating client/server security objects, querying authenticated server connection state, managing rxgk keys, crypto operations, and token creation/printing.

### Important APIs, Types, And Functions
It defines `rxgk_getkey_func`, stats flags, security object constructors, `rxgk_GetServerInfo`, key management APIs, MIC/encrypt/decrypt helpers, transport-key derivation, nonce generation, enctype comparison, and token APIs such as `rxgk_make_token`, `rxgk_print_token`, and `rxgk_print_token_and_key`.

### Control Flow
No executable flow exists in the header. The declared functions form a layered API: key creation feeds token creation and security objects; security objects use packet crypto callbacks; server token extraction uses caller-supplied `getkey`.

### State, Persistence, And Dependencies
It includes generated comerr and protocol headers plus `rxgk_types.h`, `rx_opaque.h`, and `rx_identity.h`. State is opaque to callers through `rxgk_key` and `struct rx_securityClass`.

### Integration Points
Consumers are Rx clients/servers choosing `RX_SECIDX_GK`, token issuers/printers, and services that need authenticated identity/expiry. The functions are implemented across rxgk client, server, token, util, packet, and RFC3961 crypto files.

### Risks
Crypto APIs return rxgk wire-visible error codes, so backend errors must be translated. Callers must release `rxgk_key` and opaque buffers correctly. Public exposure of low-level crypto helpers increases misuse risk outside the intended security-object flow.

### Test Signals
API tests should create server and client security objects, issue/extract tokens, derive keys, verify MIC/encryption round trips, exercise enctype choices, and validate ownership rules for returned keys and opaque buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_client.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_client.c

### Purpose
`rxgk_client.c` implements the client-side Rx security class callbacks for rxgk, including per-connection setup, packet protection, challenge response construction, packet verification, stats, and security object lifetime.

### Important APIs, Types, And Functions
The exported constructor is `rxgk_NewClientSecurityObject()`. Static callbacks in `rxgk_client_ops` include close, new connection, prepare packet, get response, check packet, destroy connection, and stats. Helpers copy/destroy private state, fill `RXGK_Authenticator`, encrypt authenticators, and pack `RXGK_Response`.

### Control Flow
A new security object copies the token master key and token. A new connection records a safe start time, reserves security overhead, stores `rxgk_cconn`, and references the object. Packet preparation updates stats, writes the low 16 bits of key number into the packet checksum field, derives a transport key, and applies MIC or encryption for AUTH/CRYPT. Challenge response decodes server nonce, copies the token, fills channel-binding authenticator data, encrypts it, packs the response into the packet, and sets the wire key number.

### State, Persistence, And Dependencies
`rxgk_cprivate` persists per security object with `k0`, enctype, level, and token. `rxgk_cconn` persists per Rx connection with start time, key number, and stats. Dependencies include Rx packet APIs, XDR generated rxgk types, `rx_opaque`, RFC3961 wrappers through public rxgk functions, and `opr_time64`.

### Integration Points
Rx calls these callbacks during connection lifecycle, challenge/response authentication, send preparation, receive verification, and stats collection. The packet work delegates to `rxgk_packet.c`.

### Risks
Challenge decoding assumes contiguous packet payload. Rekey policy is only partially implemented; stats are not reset on key-number update. `cp->enctype` is stored but not used in the shown code. Security depends on correct call-number vector export and matching server-side authenticator checks.

### Test Signals
Tests should cover object creation/destruction, challenge-response round trip, AUTH and CRYPT packet protection, bad or truncated challenge packets, key-number wrap/update handling, stats increments, clear-level behavior, and allocation-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_crypto_rfc3961.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_crypto_rfc3961.c

### Purpose
`rxgk_crypto_rfc3961.c` adapts the in-tree Kerberos RFC3961 crypto library to rxgk's opaque key API, packet/token crypto needs, transport-key derivation, nonce generation, and enctype ranking.

### Important APIs, Types, And Functions
It defines the concrete `rxgk_key_s` wrapper around a `krb5_keyblock` plus init context. Public functions implement key length lookup, make/copy/random/release key, MIC length/create/verify, encrypt/decrypt, `rxgk_derive_tk`, cipher expansion, nonce generation, and `rxgk_enctype_better`. Static helpers translate errors, map enctypes to checksum types, and implement RFC4402-style PRF+.

### Control Flow
Key creation accepts either full key bytes or random-to-key seed bytes. MIC and encryption operations create a fresh krb5 context/crypto handle per call, perform the RFC3961 operation, populate `RXGK_Data`, and destroy temporary crypto state. Transport-key derivation serializes epoch, cid, start time, and key number into a 20-byte seed, runs PRF+ to the enctype seed length, then calls random-to-key.

### State, Persistence, And Dependencies
Persistent state is the allocated rxgk key object. Other buffers and contexts are per-call. Dependencies are `afs/rfc3961.h`, Rx allocators, `rx_opaque`, `opr/time`, and generated rxgk key usage constants.

### Integration Points
Client/server packet code uses derived transport keys for per-packet MIC/encryption. Token code uses server keys to wrap tokens and random keys for printed tokens. `rxgk_util.c` queries MIC and cipher overhead.

### Risks
Most backend errors collapse to `RXGK_INCONSISTENCY`, reducing diagnostics. Checksum-type mapping is manual and must track supported enctypes. The key object stores a context for initialization/destruction only; crypto calls intentionally allocate separate contexts for thread safety. Negative local enctypes are ranked stronger by policy.

### Test Signals
Signals include known-vector RFC3961 encryption/MIC tests, key length validation for seed/full key inputs, unsupported enctype failures, PRF+ transport-key reproducibility, nonce length, cipher overhead, MIC verification failure mapping, and leak checks across all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_crypto_rfc3961.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_packet.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_packet.c

### Purpose
`rxgk_packet.c` protects and validates Rx packets for rxgk AUTH and CRYPT levels by constructing a pseudoheader, applying MIC or encryption, and reversing those operations on receipt.

### Important APIs, Types, And Functions
Public internal APIs are `rxgk_mic_packet`, `rxgk_enc_packet`, and `rxgk_check_packet`. Static helpers populate the `rxgk_header`, verify MIC packets, and decrypt encrypted packets.

### Control Flow
For AUTH sends, the plaintext payload is prefixed in memory with a pseudoheader and MICed; the MIC is written into the reserved security header before the original payload. For CRYPT sends, the pseudoheader and payload are encrypted together and replace packet data. Receive-side AUTH extracts the MIC and payload, verifies against the pseudoheader, and shrinks packet data size. Receive-side CRYPT decrypts, validates the embedded pseudoheader in constant time, writes plaintext back, and restores plaintext data size.

### State, Persistence, And Dependencies
No persistent state is stored here. It uses Rx packet read/write and security header size APIs, `rxgk_key_number`, transport-key derivation, and RFC3961 wrappers. The 16-bit wire key number is stored in the Rx packet checksum field by caller code.

### Integration Points
Client and server security callbacks call `rxgk_check_packet` with role-specific key usages. `rxgk_util.c` must reserve matching header/trailer sizes before these routines run.

### Risks
Correct packet offsets depend on Rx security header size being set exactly for the security level. Contiguous encrypted/plain buffer lengths are bounded to 16-bit packet sizes. CRYPT relies on the encrypted pseudoheader to bind epoch, cid, call number, sequence, security index, and plaintext length. CLEAR ignores invalid key-number deltas by design.

### Test Signals
Tests should cover MIC and CRYPT round trips, tampered pseudoheader/data/MIC, wrong key usage, bad security header sizes, truncated MIC/ciphertext, ciphertext expansion near 65535 bytes, key-number increments/decrements, and CLEAR packet behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_private.h -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_private.h

### Purpose
`rxgk_private.h` declares rxgk internal connection/object state, packet pseudoheader layout, statistics, and cross-file helper prototypes.

### Important APIs, Types, And Functions
Key structures are `rxgkStats`, packed `rxgk_header`, `rxgk_sprivate`, `rxgk_sconn`, `rxgk_cprivate`, and `rxgk_cconn`. Prototypes expose internal token extraction, security overhead calculation, key-number reconstruction, packet MIC/encrypt/check helpers, and enctype length lookup.

### Control Flow
The header has no executable flow. Its structures are filled by client/server security object callbacks and consumed by packet/crypto/token utilities.

### State, Persistence, And Dependencies
`rxgk_sconn` persists server connection authentication state, challenge nonce, expiry, identity, start time, key number, and token master key. `rxgk_cconn` persists client start time, key number, and stats. `rxgk_header` is explicitly packed for wire/pseudoheader crypto input.

### Integration Points
All rxgk implementation files include this header. It bridges public `rxgk.h` types with private Rx security callbacks.

### Risks
Packed layout must remain exactly compatible with the rxgk spec and crypto input. State fields such as `auth`, `challenge_valid`, and `key_number` are security sensitive and must be updated in the correct order. The comment typo `rgxk_server.c` is harmless but signals old experimental code.

### Test Signals
Static asserts or layout tests for `rxgk_header`, lifecycle tests for server/client connection state, and packet-authentication tests that mutate each pseudoheader field are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_procs.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_procs.c

### Purpose
`rxgk_procs.c` contains server-side RPC procedure implementations for optional rxgk GSS/token-combination services.

### Important APIs, Types, And Functions
When `AFS_RXGK_GSS_ENV` is defined, it defines `SRXGK_GSSNegotiate`, `SRXGK_CombineTokens`, and `SRXGK_AFSCombineTokens`.

### Control Flow
All three procedures currently return `RXGEN_OPCODE`, indicating unimplemented or unsupported operations to callers. No input is decoded here beyond rxgen-generated wrapper behavior.

### State, Persistence, And Dependencies
There is no persistent state in this file. It includes Rx, identity, public rxgk, and private rxgk headers only under the GSS build flag.

### Integration Points
Generated server stubs from `rxgk_int.xg` would call these `SRXGK_*` functions. The makefile has a placeholder for future GSSAPI linkage, consistent with these stubs being inactive/incomplete.

### Risks
If `AFS_RXGK_GSS_ENV` is enabled and clients expect negotiation or token combination, they receive opcode errors. The file is a compatibility placeholder rather than a complete service implementation.

### Test Signals
Build with and without `AFS_RXGK_GSS_ENV`. Under the flag, RPC tests should assert these operations fail with `RXGEN_OPCODE` until real implementations are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_procs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_server.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_server.c

### Purpose
`rxgk_server.c` implements server-side rxgk security class callbacks for challenge generation, response verification, token extraction, authenticated identity storage, packet protection/checking, stats, and connection teardown.

### Important APIs, Types, And Functions
The exported APIs are `rxgk_NewServerSecurityObject()` and `rxgk_GetServerInfo()`. Static callbacks populate `rxgk_server_ops`: close, new connection, prepare packet, check authentication, create/get challenge, check response, check packet, destroy connection, and stats. Helpers handle no-auth reset, expiry checks, challenge reads, token processing, identity conversion, authenticator decryption, and constant-time authenticator checks.

### Control Flow
New server connections start unauthenticated with invalid placeholder level/expiry. Challenge creation generates and stores a random nonce; `GetChallenge` XDR-encodes it into the packet. `CheckResponse` decodes the response, decrypts/extracts the token using the configured `getkey`, checks expiry, stores the client start time, decrypts the authenticator with the derived transport key, validates nonce/level/epoch/cid/call vector length, reserves security overhead, imports call numbers, and marks the connection authenticated.

### State, Persistence, And Dependencies
Server object state is `rxgk_sprivate` with key callback and rock. Per-connection `rxgk_sconn` stores auth state, challenge, expiry, identity, stats, start time, key number, and `k0`. Dependencies include Rx security APIs, generated XDR rxgk types, `rx_identity`, `opr_time64`, packet helpers, token helpers, and RFC3961 wrappers.

### Integration Points
Rx invokes these callbacks for server authentication and packet handling. Application code can call `rxgk_GetServerInfo()` after authentication to obtain level, expiry, and a copied remote identity.

### Risks
Response decoding assumes contiguous packet data. On any response failure, `sconn_set_noauth()` clears key/identity and invalidates auth. Compound identities are not supported. Token lifetime/bytelife are parsed but ignored for rekeying. Constant-time comparison protects only selected authenticator fields; appdata is ignored.

### Test Signals
Tests should cover successful challenge-response, bad nonce/epoch/cid/level, expired tokens, getkey failures, malformed token containers, identity kinds and compound rejection, packet checks before auth, stats flags, key-number updates, and `rxgk_GetServerInfo()` ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_token.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_token.c

### Purpose
`rxgk_token.c` creates, wraps, unwraps, decrypts, and extracts rxgk tokens and printed tokens.

### Important APIs, Types, And Functions
Public APIs are `rxgk_make_token`, `rxgk_print_token`, `rxgk_print_token_and_key`, and internal `rxgk_extract_token`. Static helpers map `RXGK_TokenInfo` to `RXGK_Token`, XDR-pack tokens and containers, encrypt/decrypt token blobs, unpack containers, and share common token creation logic.

### Control Flow
Token creation copies token info, inserts `K0` and identities, XDR-encodes the token, encrypts it with the service key using `RXGK_SERVER_ENC_TOKEN`, wraps it in `RXGK_TokenContainer` with kvno/enctype, and XDR-encodes the container. Extraction decodes the container, validates kvno/enctype, obtains the service key with `getkey`, decrypts the token blob, and XDR-decodes `RXGK_Token`.

### State, Persistence, And Dependencies
No global state exists. Outputs are caller-owned `rx_opaque` buffers or XDR-allocated token contents. Printed-token helpers generate random K0 bytes and return an `rxgk_key` for caller ownership. Dependencies include generated XDR rxgk types, `rx_opaque`, `opr_time`, and crypto helpers.

### Integration Points
Servers use `rxgk_extract_token()` during response verification. Token issuers use `rxgk_make_token()` for identity-bearing tokens and `rxgk_print_token*()` for printed tokens with empty identities and default lifetime/bytelife.

### Risks
`rxgk_make_token()` deliberately rejects empty identity lists to avoid accidental printed tokens. Printed tokens set expiration to `RXGK_NEVERDATE` and override lifetime/bytelife defaults. Error paths must avoid freeing caller-owned identity arrays while freeing XDR-owned token contents. `decrypt_token()` only accepts positive kvno/enctype values.

### Test Signals
Tests should round-trip normal and printed tokens, reject zero identities in `rxgk_make_token`, reject invalid kvno/enctype, simulate getkey/decrypt failures, verify default printed-token metadata, and run leak checks around XDR free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_types.h -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_types.h

### Purpose
`rxgk_types.h` exposes the minimal public rxgk type surface needed before including the full rxgk API.

### Important APIs, Types, And Functions
It defines `rxgk_key` as an opaque pointer to `struct rxgk_key_s`.

### Control Flow
There is no executable flow. The opaque typedef allows public APIs to pass keys without exposing the RFC3961 backend representation.

### State, Persistence, And Dependencies
The concrete state is defined in `rxgk_crypto_rfc3961.c`. Callers can only hold and pass the pointer and must release it through `rxgk_release_key()`.

### Integration Points
Included by `rxgk.h` and installed as a public header. It decouples token/security-object APIs from crypto backend internals.

### Risks
Because `rxgk_key` is a pointer type, NULL is possible and misuse is not type-prevented. ABI depends on keeping the struct incomplete to external callers.

### Test Signals
Public-header compile tests should ensure users can declare `rxgk_key` and call API functions without including private crypto headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_util.c -->
## sources/distributed-fs/openafs/src/rxgk/rxgk_util.c

### Purpose
`rxgk_util.c` provides common rxgk helpers for reserving per-packet security overhead and reconstructing full key numbers from truncated wire values.

### Important APIs, Types, And Functions
`rxgk_security_overhead()` sets Rx security header/trailer reservation for CLEAR, AUTH, and CRYPT levels. `rxgk_key_number()` maps a 16-bit packet checksum field and local 32-bit key number to the peer's effective 32-bit key number.

### Control Flow
Security overhead returns no reservation for CLEAR, reserves MIC length as header for AUTH, and reserves `rxgk_header` plus max crypto trailer expansion for CRYPT. Key-number reconstruction compares low 16 bits and accepts same, +1, or -1 deltas, rejecting wrap beyond 0 or `MAX_AFS_UINT32` and other jumps.

### State, Persistence, And Dependencies
The functions mutate only the given Rx connection's security size fields and caller-provided output key number. They depend on crypto helpers for MIC length and cipher overhead and on Rx packet/security APIs.

### Integration Points
Client/server new-connection and successful-authentication paths call `rxgk_security_overhead()` before packet processing. Packet receive paths use `rxgk_key_number()` before deriving transport keys.

### Risks
Incorrect overhead reservation breaks packet offsets in `rxgk_packet.c`. The key-number algorithm intentionally only allows one-step changes, so lost rekey synchronization yields `RXGK_BADKEYNO`. CLEAR connections ignore key-number errors higher up, but this helper still reports them.

### Test Signals
Tests should assert reserved sizes by level/enctype, invalid level handling, MIC length failures, cipher overhead failures, key number same/+1/-1 behavior, low-16-bit wrap cases, and out-of-range wrap rejections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgk/rxgk_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/Makefile.in -->
## sources/distributed-fs/openafs/src/rxkad/Makefile.in

### Purpose
`rxkad/Makefile.in` builds the traditional rxkad security library, generated error/header files, installable public headers, and test utility targets.

### Important APIs, Types, And Functions
Primary targets are `all`, `generated`, `depinstall`, static `librxkad.a`, shared `liboafs_rxkad.la`, PIC `librxkad_pic.la`, `tcrypt`, `install`, `dest`, and `clean`. Generated files come from `rxkad_errs.et` through `COMPILE_ET_C` and `COMPILE_ET_H`.

### Control Flow
The build links rxkad client/server/common, fcrypt, packet crypt, ticket, ticket5, CRC, and generated error objects against comerr, rx, opr, and RFC3961/hcrypto libraries. Dependency rules install public headers into `TOP_INCDIR`.

### State, Persistence, And Dependencies
Persistent outputs include libraries, generated `rxkad_errs.c`, generated `rxkad.h`, installed `fcrypt.h`, `rxkad_prototypes.h`, `rxkad_convert.h`, and stats header. `clean` also recurses into `test`.

### Integration Points
This is the build bridge between legacy rxkad code, Heimdal-derived ticket/DER support, and the OpenAFS Rx library. `ticket5.lo` includes generated/rewritten v5 sources and suppresses deprecated declaration warnings.

### Risks
The makefile mixes generated headers with source headers, so dependency order matters. `crypt_conn.c` and `bg-fcrypt.c` provide overlapping packet crypto implementations depending on build context. Install target omits some depinstalled headers such as stats/convert compared with `depinstall`.

### Test Signals
Clean rebuilds, generated header regeneration, static/shared/PIC library link checks, `tcrypt` build/run, install/dest staging, and test-directory clean behavior are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/asn1_err.h -->
## sources/distributed-fs/openafs/src/rxkad/asn1_err.h

### Purpose
`asn1_err.h` is a generated com_err header for Heimdal ASN.1/DER error codes used by rxkad Kerberos v5 ticket handling.

### Important APIs, Types, And Functions
It declares `initialize_asn1_error_table_r()`, `initialize_asn1_error_table()`, alias `init_asn1_err_tbl`, enum `asn1_error_number`, `ERROR_TABLE_BASE_asn1`, and `COM_ERR_BINDDOMAIN_asn1`.

### Control Flow
There is no runtime implementation here. Consumers initialize the error table before translating ASN.1 errors through com_err.

### State, Persistence, And Dependencies
The header has no mutable state and forward-declares `struct et_list`. Numeric error values are persistent ABI/protocol diagnostics.

### Integration Points
DER/ticket code and com_err users include this to map parser/encoder failures such as bad length, overrun, missing fields, constraints, or BER/indefinite encoding issues.

### Risks
Because it is generated, manual edits can be overwritten. Error table base must remain stable or existing error interpretation changes.

### Test Signals
Build tests should ensure the generated com_err source matches this header and runtime tests should initialize and stringify representative ASN.1 errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/asn1_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/bg-fcrypt.c -->
## sources/distributed-fs/openafs/src/rxkad/bg-fcrypt.c

### Purpose
`bg-fcrypt.c` implements the rxkad fcrypt block cipher/key schedule and Rx packet encryption/decryption using CBC mode over packet fragments.

### Important APIs, Types, And Functions
Public functions are `fc_keysched`, `fc_ecb_encrypt`, `fc_cbc_encrypt`, `rxkad_EncryptPacket`, and `rxkad_DecryptPacket`. Static inline helpers implement 16-round Feistel ECB encrypt/decrypt and CBC encrypt/decrypt. Large static S-box tables define the round function.

### Control Flow
`fc_keysched()` compresses parity bits from an 8-byte key into 56 bits, emits 16 rotated 32-bit round schedules, and records stats. ECB applies the Feistel rounds forward or reverse. CBC XORs with IV, encrypts/decrypts blockwise, updates IV, and copies eight-byte blocks. Packet encryption zeroes part of the rxkad security header, then walks `wirevec` fragments from index 1, encrypting in place; decryption reverses that walk.

### State, Persistence, And Dependencies
Persistent static state is only S-box constants. Runtime state is caller-provided schedules, IV copies, packet buffers, and rxkad stats counters. Kernel and user builds use different includes and endian helpers.

### Integration Points
rxkad client/server/common code calls these packet crypto functions for encrypted security levels. The Makefile builds `fcrypt.c` normally; this file also contains a standalone `TEST` harness with known vectors and performance timing.

### Risks
Comments note intentional over-read/over-write assumptions for partial CBC blocks, relying on packet layout. Endianness and schedule compatibility are critical; schedules are not interchangeable with other implementations. Legacy fcrypt is weak by modern standards but required for rxkad compatibility.

### Test Signals
Use the built-in known vectors under `TEST`, packet encrypt/decrypt round trips across fragmented packets and partial lengths, endian-platform tests, stats increments, and kernel/user build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/bg-fcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/crc.c -->
## sources/distributed-fs/openafs/src/rxkad/crc.c

### Purpose
`crc.c` implements table initialization and incremental CRC32 update helpers used by rxkad ticket/lifetime code.

### Important APIs, Types, And Functions
`_rxkad_crc_init_table()` lazily fills a 256-entry table using polynomial `0xEDB88320`. `_rxkad_crc_update()` updates a caller-supplied CRC accumulator over a byte buffer.

### Control Flow
Initialization returns immediately after the static flag is set. Otherwise it computes each table entry by eight shift/xor iterations. Update walks each byte, indexes the table with `(res ^ byte) & 0xff`, shifts the accumulator, and returns the masked 32-bit result.

### State, Persistence, And Dependencies
The static table and initialization flag persist process-wide. Dependencies include Rx/XDR and rxkad headers, though the implementation itself is standalone CRC logic.

### Integration Points
Used by rxkad code that needs the Heimdal-derived CRC primitive, especially Kerberos-related checksum handling.

### Risks
The lazy initialization flag is not synchronized, so concurrent first use could race while computing identical values. Callers must ensure initialization before update or receive zero-table results.

### Test Signals
Known CRC32 vectors, update-in-chunks equivalence, update-before-init behavior, and thread sanitizer first-use tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/crypt_conn.c -->
## sources/distributed-fs/openafs/src/rxkad/crypt_conn.c

### Purpose
`crypt_conn.c` provides packet encryption/decryption routines for the rxkad security object using the `rx_data()` fragment accessor path.

### Important APIs, Types, And Functions
It defines `rxkad_DecryptPacket()` and `rxkad_EncryptPacket()` for `XPRT_RXKAD_CRYPT`. Both call `fc_cbc_encrypt()` with either `FCRYPT_DECRYPT` or `FCRYPT_ENCRYPT`.

### Control Flow
Each function copies the caller IV into a local XOR vector, records byte stats using the security object's private type, then iterates packet data fragments by index. For encryption it writes zero into the second 32-bit word of the packet security header before CBC processing. Each loop processes the minimum of remaining length and fragment length.

### State, Persistence, And Dependencies
No local persistent state exists. Packet contents are mutated in place. Dependencies include Rx packet APIs, rxkad stats, `private_data.h`, and fcrypt key schedule/IV types.

### Integration Points
rxkad uses these functions behind packet processing callbacks for crypt-level connections. This file is separate from `bg-fcrypt.c`'s wirevec implementation, reflecting alternate platform/build paths.

### Risks
The loop breaks silently if `rx_data()` returns no data before `len` reaches zero, yet still returns success. Integrity checksum code is commented out, so the security header checksum word is always zero. Fragment alignment and block-size assumptions are delegated to fcrypt.

### Test Signals
Tests should include multi-fragment packets, early missing-fragment cases, partial final lengths, stats increments, header zeroing, and encrypt/decrypt round trips compared with `bg-fcrypt` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/crypt_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/der-protos.h -->
## sources/distributed-fs/openafs/src/rxkad/der-protos.h

### Purpose
`der-protos.h` is a generated Heimdal DER/ASN.1 prototype header vendored under rxkad for Kerberos v5 ticket support.

### Important APIs, Types, And Functions
It declares fuzzer hooks, copy/free/decode/encode routines for Heimdal ASN.1 types, DER primitive getters and putters, length calculators, tag/class/type name mapping, OID and integer parsing/printing, comparison helpers, and `heim_any` helpers.

### Control Flow
The header has no executable flow. The declared APIs follow DER conventions: decode/get functions consume buffers and return consumed sizes, put/encode functions write backwards into bounded buffers, free functions release nested allocations, and length functions compute encoded sizes.

### State, Persistence, And Dependencies
It has no state, uses an include guard, supports C++ linkage, and is hidden under `#ifndef DOXY`. It depends on Heimdal ASN.1 typedefs from surrounding headers such as `der.h` and generated v5 headers.

### Integration Points
rxkad Kerberos v5 ticket code includes this through `der.h` to encode/decode tickets and authorization data. Fuzzer hooks allow generated ASN.1 fuzz infrastructure to drive decoders.

### Risks
As generated API surface, manual drift from implementation sources causes compile/link mismatches. Many routines allocate memory through Heimdal conventions, so callers must match decode/copy calls with the correct free functions.

### Test Signals
Compile/link coverage against DER implementation, ASN.1 encode/decode round trips, malformed length/tag tests, memory-leak checks for every decode/free pair, and fuzzer builds are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/der-protos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/der.h -->
## sources/distributed-fs/openafs/src/rxkad/der.h

### Purpose
`der.h` defines core Heimdal DER tag classes, tag types, universal tag constants, time helper structures, and DER helper prototypes used by rxkad Kerberos v5 code.

### Important APIs, Types, And Functions
It defines `Der_class`, `Der_type`, `MAKE_TAG`, universal tag constants, `ASN1_INDEFINITE`, `heim_der_time_t`, `heim_ber_time_t`, forward declaration `struct asn1_template`, includes `der-protos.h`, and declares internal helpers `_heim_fix_dce`, `_heim_der_set_sort`, and `_heim_time2generalizedtime`.

### Control Flow
No executable flow exists. Macros and enums encode DER tag bytes and classify primitive/constructed ASN.1 objects.

### State, Persistence, And Dependencies
The header has no mutable state and is guarded by `__DER_H__`. It requires ASN.1 type definitions such as `heim_octet_string` from included/generated Heimdal headers in the rxkad build.

### Integration Points
Ticket v5 DER code uses these definitions to parse and emit Kerberos structures. `der-protos.h` supplies the large generated function surface.

### Risks
Universal tag constants include unsupported aliases and a duplicate numeric value for `UT_UniversalString`/`UT_GraphicString`, matching ASN.1 numbering but easy to misuse. `ASN1_INDEFINITE` is a sentinel, not a normal length.

### Test Signals
Tests should validate tag construction, DER length/tag parsing, time conversion, SET sorting, DCE length fixups, and encode/decode compatibility with Kerberos ticket fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxkad/der.h -->
