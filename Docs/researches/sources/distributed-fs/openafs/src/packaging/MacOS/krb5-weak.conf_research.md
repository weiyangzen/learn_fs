<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/krb5-weak.conf -->
# sources/distributed-fs/openafs/src/packaging/MacOS/krb5-weak.conf

## Purpose
Provides a minimal Kerberos configuration snippet for macOS packaging that enables weak cryptography. It is shipped into the OpenAFS private configuration area so legacy AFS/Kerberos workflows can still operate when they require older encryption types.

## Important APIs, Types, And Functions
The file is not executable code. It contains a `[libdefaults]` section with `allow_weak_crypto = true`, which is interpreted by MIT/Heimdal Kerberos libraries through normal krb5 configuration loading.

## Control Flow
There is no control flow in the file itself. `pkgbuild.sh.in` copies it into `private/var/db/openafs/etc/krb5-weak.conf` during package-root creation, where OpenAFS scripts or user instructions can point Kerberos tooling at it.

## State And Persistence
The persistent state is the installed config file. Enabling weak crypto affects processes that include this config in their krb5 configuration chain; it does not modify the system krb5 config directly.

## Dependencies And Integration Points
It depends on Kerberos libraries honoring `allow_weak_crypto`. It integrates with macOS installer packaging and legacy OpenAFS authentication paths that may still need DES/weak enctype compatibility.

## Risks And Test Signals
The explicit security risk is enabling weak cryptography. Packaging tests should verify the file is installed only where intended, while authentication tests should confirm legacy cells work when this config is used and modern Kerberos behavior remains unaffected when it is not referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/krb5-weak.conf -->
