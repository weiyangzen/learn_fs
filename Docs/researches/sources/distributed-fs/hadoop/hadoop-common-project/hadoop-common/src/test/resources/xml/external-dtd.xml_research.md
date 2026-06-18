# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/external-dtd.xml

## Purpose
`external-dtd.xml` is an XML parser security fixture that references an external DTD named `address.dtd`.

## Important Structure
The document declares `<!DOCTYPE address SYSTEM "address.dtd">` and contains a simple `address` element with `name`, `company`, and `phone` children.

## Control Flow
Parser tests load this file to verify how external DTD resolution is handled. Hardened parser configurations should prevent unintended external resource access where appropriate.

## State And Persistence
It is static XML data only. Any external resolution behavior is performed by the parser/test harness at runtime.

## Dependencies And Integration Points
It integrates with XML parser tests and security hardening around external entities and DTD loading.

## Risks
External DTD processing can lead to XXE or filesystem/network access if parser settings are unsafe. This fixture is useful precisely because it can expose accidental external resolution.

## Test Signals
Expected signals are either a controlled rejection of external DTD resolution or successful parsing only when a test explicitly permits and supplies the external DTD.
