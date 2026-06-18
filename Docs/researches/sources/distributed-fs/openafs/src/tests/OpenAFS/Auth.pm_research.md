# sources/distributed-fs/openafs/src/tests/OpenAFS/Auth.pm

## Purpose
`Auth.pm` is the newer Perl authentication abstraction for OpenAFS tests. It creates backend-specific authentication objects for MIT Kerberos, Heimdal, or kaserver, generates Kerberos/OpenAFS key material where supported, and obtains test credentials.

## Important APIs, types, and functions
Package `OpenAFS::Auth` exposes `create`, `new`, `_lookup_cell_name`, `make_keyfile`, `make_krb_config`, `debug`, and `check_program`. Subpackages `OpenAFS::Auth::MIT`, `OpenAFS::Auth::Heimdal`, and `OpenAFS::Auth::Kaserver` implement `_sanity_check`, `make_keyfile`, and `authorize`; MIT additionally has `_prepare_make_keyfile`.

## Control flow
`create` maps a type to a backend class and constructs it. `new` fills defaults such as admin principal, AFS principal, kvno, keytab, and realm, blesses the object, and runs backend sanity checks. `make_krb_config` writes a krb5 config file for the test realm/cell. MIT keyfile setup checks programs, initializes kadmin state, adds principals, extracts keytabs, ensures AFS config files exist, and runs `asetkey`. `authorize` paths run `kinit` plus `aklog`, Heimdal's `afslog`, or kaserver `klog`.

## State and persistence behavior
The object stores backend configuration in memory. It writes Kerberos config, creates Kerberos principals/keytabs, writes OpenAFS KeyFile material through `asetkey` or `bos addkey`, and obtains Kerberos tickets/AFS tokens in the user's credential cache/PAG context.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, `OpenAFS::ConfigUtils::run`, OpenAFS tools (`asetkey`, `aklog`, `tokens`, `kas`, `klog`, `bos`), Kerberos tools (`kadmin.local`, `kdb5_util`, `kinit`), and generated test path configuration.

## Risks
Most commands are shell strings composed from object fields, so quoting and spaces in paths/principals are unsafe. Several operations are privileged and destructive to test Kerberos/OpenAFS state. Heimdal `make_keyfile` is explicitly unimplemented. Backend selection and duplicated legacy modules can confuse loaders.

## Test signals
Test `create` for MIT/Heimdal/kaserver and invalid types, missing program/keytab/realm checks, krb5 config output, MIT principal/keytab/keyfile creation in a disposable realm, authorization flows, debug output, and failure rollback expectations through `ConfigUtils`.
