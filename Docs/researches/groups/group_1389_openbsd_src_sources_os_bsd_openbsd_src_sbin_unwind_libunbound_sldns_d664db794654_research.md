# Group Research: group_1389_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_sldns_d664db794654

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.c

`keyraw.c` implements raw DNSSEC key helpers over DNSKEY wire-format RDATA. It computes DNSKEY public-key sizes for DSA, RSA, GOST, ECDSA, Ed25519, and Ed448 algorithms when compiled in, and implements the DNSSEC key-tag calculation including the RSAMD5 legacy special case.

When OpenSSL support is enabled, the file converts raw DNSKEY public key material into OpenSSL key objects. RSA and DSA parsing extracts BIGNUM components from DNS wire layout, then builds either legacy RSA/DSA objects or OpenSSL 3 `EVP_PKEY` objects through `OSSL_PARAM_BLD`. ECDSA handling chooses the P-256/P-384 group and prepends the uncompressed-point marker before importing. GOST, Ed25519, and Ed448 use fixed ASN.1 public-key prefixes around the raw DNSKEY bytes.

The optional GOST path manages an OpenSSL engine reference with `sldns_key_EVP_load_gost_id()` and `sldns_key_EVP_unload_gost()`. The file is heavily feature-macro gated, so supported algorithms depend on compile-time crypto options and OpenSSL/LibreSSL API availability.

Most functions are defensive about minimum lengths and expected encoded key sizes. Ownership is important: conversion helpers free partially built BIGNUM/OpenSSL state on errors, and successful legacy `EVP_PKEY_assign_*` paths transfer ownership into the returned `EVP_PKEY`.

The file also provides `sldns_digest_evp()`, a small wrapper around OpenSSL EVP digest initialization, update, and finalization.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.h

`keyraw.h` declares the raw DNSSEC key API. The non-OpenSSL surface covers DNSKEY public-key size calculation and DNSSEC key-tag calculation directly from uncompressed wire-format RDATA.

When SSL support is compiled in, the header exposes OpenSSL conversion helpers for DSA, RSA, GOST, ECDSA, Ed25519, and Ed448 public keys, plus the generic EVP digest wrapper. Legacy RSA/DSA object-returning functions are hidden when the OpenSSL 3 parameter-builder path is available.

The header is the narrow contract between DNS wire/RDATA parsing and crypto verification code: callers provide raw DNSKEY bytes and receive OpenSSL public-key objects or simple DNSSEC metadata values.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/keyraw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.c

`parse.c` implements low-level tokenizers for DNS-style presentation text from either `FILE*` streams or `sldns_buffer` objects. It understands zone-file features: semicolon comments, quoted strings, escaped characters, parenthesized multiline records, configurable delimiters, CR normalization, and optional line-number tracking.

The file-based path is centered on `sldns_fget_token_l()`, with wrappers for default line tracking. It skips comments, collapses continuation newlines inside parentheses to spaces, avoids returning blank-only lines as tokens, enforces caller-provided limits, and returns errors for unbalanced parentheses or overlong tokens.

The buffer-based path mirrors that behavior with `sldns_bget_token_par()`. It can preserve parenthesis state across calls through a caller-provided `par` pointer, which is used by higher-level RR parsing for multi-token RDATA handling.

Keyword helpers read `keyword<delimiter>data` pairs from files or buffers. Skip helpers advance over sets of characters for both backends, and `sldns_bgetc()` provides a `getc()` equivalent over `sldns_buffer`.

This file is foundational for zone-file and resolver-config parsing; it deliberately returns tokens rather than interpreting DNS RDATA semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.h

`parse.h` declares the low-level parsing/tokenization API. It defines delimiter sets for normal DNS whitespace parsing, newline-preserving parsing, and space skipping, plus maximum line and keyword lengths.

The header defines zone-file directive IDs for `$TTL`, `$ORIGIN`, and `$INCLUDE`, with the directive lookup table implemented in `parse.c`.

The public API covers file token reads, line-number-aware token reads, buffer token reads with optional cross-call parenthesis state, keyword/data extraction, single-character buffer reads, and skip-character helpers. The buffer-token API documents the key contract: callers that pass a parenthesis state must verify it returns to zero after the complete record is parsed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.c

`parseutil.c` implements shared parsing and encoding utilities used by text-to-wire and wire-to-text paths. It includes generic lookup-table search by name or ID, UTC time conversion helpers, period/duration parsing, hex digit parsing, escaped-character parsing, and base32/base64 codecs.

The time code provides `sldns_mktime_from_utc()` as a portable `timegm()` equivalent. For 32-bit `time_t` builds it includes 64-bit-safe calendar conversion so DNSSEC serial-arithmetic timestamps can still be interpreted relative to a supplied `now`.

`str2period` parses DNS TTL-style duration strings with `s`, `m`, `h`, `d`, and `w` suffixes, accumulating into a 32-bit value with explicit overflow reporting. Escape parsing accepts either a three-decimal-octet escape or a single escaped literal.

The base32 code supports normal and extended-hex alphabets, padded output, and padded input validation. The base64 code supports standard base64 and unpadded base64url, skips non-base64 characters in the standard decoder, and has a helper to detect characters illegal in base64url form.

These utilities keep scalar, time, escape, and binary text encodings out of the RR-specific parser code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.h

`parseutil.h` declares shared parse utility types and functions. `sldns_lookup_table` is the common integer/name mapping structure used for RR classes, algorithms, errors, and similar tables.

The API covers lookup-table search, UTC `struct tm` conversion, RFC1982-style serial timestamp conversion, TTL/period parsing with overflow reporting, hex digit conversion, base64/base64url and base32/base32hex size calculation plus encode/decode functions, and escaped-character parsing.

The header is used by both parser and formatter modules, so it forms the common support layer for DNS presentation syntax and binary encodings.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parseutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/pkthdr.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/pkthdr.h

`pkthdr.h` defines DNS packet header constants, flag masks, and accessor macros for raw wire buffers. It covers the 12-byte DNS header, query ID, section counts, and all standard first/second flag-octet bits: QR, opcode, AA, TC, RD, RA, Z, AD, CD, and RCODE.

The macros read and update raw header bytes in place, using `sldns_read_uint16()` and `sldns_write_uint16()` for multi-byte fields. They assume the caller has a valid DNS header buffer.

The header also defines enums for packet sections, opcodes, and base RCODEs. It contains no functions; it is a low-level wire-buffer convenience layer used by packet parsing, construction, and mutation code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/pkthdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.c

`rrdef.c` implements DNS RR schema metadata. It defines the class lookup table and a large descriptor table mapping RR type codes to presentation names, minimum/maximum RDATA field counts, field RDF types, variable trailing RDF type, compression eligibility, and number of DNAME fields.

The descriptor table covers classic RFC1035 types, DNSSEC types, NSEC3, TLSA/SMIMEA, CDS/CDNSKEY, OPENPGPKEY, CSYNC, ZONEMD, SVCB/HTTPS, ILNP/EUI/URI/CAA, TKEY/TSIG, transfer/query pseudo-types, RESINFO, and DLV/TA. Unassigned gaps are represented as `TYPE###` descriptors with unknown/raw-style RDATA.

`LDNS_RDATA_FIELD_DESCRIPTORS_COMMON` allows direct array lookup for the contiguous low-numbered range; higher or split-out values are found by scanning. Unknown types fall back to descriptor zero.

The exported helpers return descriptors, minimum and maximum field counts, RDF type for a field index, RR type by textual name including `TYPE###`, and class by textual name including `CLASS###`. This file is the schema source used by `str2wire.c` to decide how to parse RDATA fields and where DNS name compression is allowed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.h

`rrdef.h` declares DNS RR constants, enums, and descriptor APIs. It defines maximum label/domain sizes, RR overhead, DNSSEC key flag bits, RDF byte-size constants, NSEC/APL constants, and the externally visible RR class lookup table.

The RR type enum includes standard types, DNSSEC, modern service and security types, query pseudo-types, and the full 0-65535 range bounds. The RDF type enum describes how individual RDATA fields are parsed and formatted: domain names, integers, addresses, strings, base encodings, NSEC bitmaps, algorithms, time/period values, TSIG fields, LOC/WKS/NSAP/ATMA/IPSECKEY, NSEC3 components, ILNP/EUI values, CAA tags, long strings, and SVCB parameters.

The header also defines DNSSEC algorithm IDs, DS hash IDs, CERT algorithm IDs, EDNS option codes, EDE codes, TSIG/TKEY extended errors, and BADCOOKIE.

`struct sldns_rr_descriptor` is the central schema record for a type: type code, name, min/max fields, wireformat RDF list, variable RDF type, compression policy, and DNAME count. The declared functions expose descriptor lookup and name-to-type/class conversion.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.c

`sbuffer.c` implements the non-inline parts of the `sldns_buffer` memory-buffer API. `sldns_buffer_new()` allocates a dynamic buffer with position zero, limit equal to capacity, and clear status. `sldns_buffer_new_frm_data()` replaces an existing non-fixed buffer’s data with an allocated copy, while `sldns_buffer_init_frm_data()` wraps caller-owned data as a fixed, non-resizable buffer.

Capacity management is handled by `sldns_buffer_set_capacity()` and `sldns_buffer_reserve()`. Dynamic reserve grows capacity by 1.5x or to the exact required size, then resets the limit to capacity.

`sldns_buffer_printf()` writes formatted output at the current position if the status is OK, marking the buffer failed on `vsnprintf()` error. `sldns_buffer_free()` frees dynamic data and the buffer object, and `sldns_buffer_copy()` copies up to the destination capacity, silently truncating if needed, then flips the destination for reading.

The file is small because most typed read/write and position operations are inline in `sbuffer.h`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.h

`sbuffer.h` defines `sldns_buffer`, a Java-NIO-style byte buffer with position, limit, capacity, data pointer, fixed/resizable flag, and sticky status-error flag.

It provides inline endian-safe integer helpers for unaligned network-order 16-bit, 32-bit, and 48-bit reads/writes. These are also used by raw DNS header and RR accessors elsewhere.

The inline buffer API covers invariants, clear/flip/rewind, position and limit management, capacity query, pointer access, remaining/available checks, raw byte writes, string writes, typed writes for 8/16/32/48-bit values, raw reads, and typed reads for 8/16/32-bit values. Most operations use assertions for bounds checking, so callers are expected to verify availability or reserve space first in production builds.

The declared non-inline API covers allocation, wrapping/copying data, resizing/reserving, formatted printing, freeing, and buffer copying. This header is the shared low-level byte-buffer abstraction used by the parser and wire conversion code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.c

`str2wire.c` converts DNS presentation-format names, RRs, and individual RDATA fields into DNS wire format. It returns structured parse errors that combine an error code with an input offset.

Domain-name parsing builds uncompressed wire-format names, handles escaped octets/literals, validates label/domain limits, detects relative names, and appends an origin when requested. `@` and empty owner handling use origin, previous owner, or root fallback depending on parse context.

The RR parser reads owner, optional TTL, optional class, and type, then writes the wire RR header. RDATA parsing is driven by the descriptor table from `rrdef.c`; it handles per-field delimiters, quoted strings, parenthesized multiline input, variable field counts, HIP and length-prefixed data special cases, and RFC3597 `\# <length> <hex>` unknown-RR syntax. It writes RDLENGTH after parsing.

SVCB/HTTPS receive substantial special handling. The parser recognizes named and numeric SvcParamKeys, encodes mandatory/alpn/no-default-alpn/port/ipv4hint/ech/echconfig/ipv6hint/dohpath and generic key values, supports quoted/unescaped values, sorts SvcParams by numeric key, and optionally compiles semantic checks for duplicates and mandatory constraints.

`fp2wire_rr_buf()` reads one logical zone-file RR through the tokenizer, handles `$ORIGIN`, `$TTL`, `$INCLUDE`, other directives, previous-owner state, line numbers, and default TTL updates. There are also safe raw-wire accessors for type, class, TTL, RDLENGTH, and RDATA pointers.

The RDF converters cover integers, IPv4/IPv6 addresses, character strings, APL, base64/base32hex, hex, NSEC bitmaps, RR type/class names, CERT algorithms, DNSSEC algorithms, TSIG errors, DNSSEC times, TSIG 48-bit times, periods, LOC, WKS service bitmaps, NSAP, ATMA, IPSECKEY, NSEC3 salt, ILNP64, EUI48/EUI64, CAA tags, long strings, HIP, and 16-bit-length-prefixed data.

The file is tightly coupled to `parse.c`, `parseutil.c`, `rrdef.c`, `wire2str` lookup tables, and `sbuffer`. It is the main ingestion path for zone-file text, resolver hints, local data, and any configuration that supplies DNS RRs in presentation form.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.h

`str2wire.h` declares the text-to-wire DNS conversion API. It defines IPv4/IPv6 address lengths, the 64 KiB RR buffer recommendation, default TTL, SVCB key constants, SVCB parameter limits, and the parse-error code namespace.

The public API converts domain names, full RRs, question-only RRs, file-stream RRs, and individual RDF values into wire format. Full RR output layout is explicitly documented as uncompressed owner name followed by type, class, TTL, RDLENGTH, and RDATA; helper accessors retrieve those fields safely despite possible unaligned storage.

`struct sldns_file_parse_state` stores `$ORIGIN`, previous owner name, current default TTL, and line number across zone-file reads. `sldns_fp2wire_rr_buf()` uses this state to honor zone-file directives and owner-name inheritance.

The header exposes converters for every RDF type implemented in `str2wire.c`, including specialized DNSSEC, LOC, WKS, IPSECKEY, NSEC3, ILNP/EUI, CAA, HIP, and length-prefixed data formats. It also declares `sldns_get_errorstr_parse()` and whitespace stripping for callers that need diagnostics or directive handling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/str2wire.h -->