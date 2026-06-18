# sources/distributed-fs/ceph-client/lib/build_OID_registry

## Purpose

`sources/distributed-fs/ceph-client/lib/build_OID_registry` is a Perl build helper that generates a C registry for ASN.1 object identifiers declared in an input header. It parses enum-style OID declarations and writes encoded OID data plus lookup tables.

## Important APIs, Types, and Functions

The script has no reusable Perl functions; its public interface is the command line `build_OID_registry <in-h-file> <out-c-file>`. It emits `oid_index`, `oid_data`, and `oid_search_table` C definitions keyed by `enum OID` names. It uses `Cwd::abs_path`, `@names`, `@oids`, `@lengths`, `@indices`, `@encoded_oids`, and `@hash_values`.

## Control Flow

The script validates that exactly two arguments were passed, resolves `$ENV{srctree}`, scans the input file for `OID_NAME, /* dotted.oid */` lines, opens the output C file, computes DER-style base-128 encoded lengths and offsets, emits an index table sized as `unsigned char` or `unsigned short`, encodes each OID component into octets, computes a compact hash, sorts lookup entries by hash, encoded length, and reverse byte content, then emits the search table.

## State and Persistence Behavior

All state is process-local arrays. The only persistent output is the generated C file. The generated header comment strips the absolute source-tree prefix when `srctree` is set.

## Dependencies and Integration Points

The script depends on Perl, `bc` for base-2 conversion, `srctree` in the environment, and the expected OID declaration format. It integrates with kernel build rules that generate static OID lookup data consumed by ASN.1 or key/certificate code.

## Risks and Edge Cases

The input regex is narrow and will ignore declarations that do not match the exact comment format. It shells out to `bc` for every component beyond the first two, so missing `bc` or unusual environment behavior breaks generation. Very large OID data changes the index type. Hash collisions are handled by ordering but consumers must compare encoded bytes, not trust the hash alone.

## Test Signals

Useful signals are generation from a known OID header, byte-for-byte stable output, correct base-128 encoding for multi-octet components, behavior when total length crosses 255, missing/wrong argument exit status, and build integration that compiles the generated C output.

## Read Coverage

Source read size: 218 lines, 5098 bytes.
