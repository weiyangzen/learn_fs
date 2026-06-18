# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/entity-dtd.xml

## Purpose
`entity-dtd.xml` is an XML parser test fixture with an inline DTD and entity declaration.

## Important Structure
It declares an internal DTD for `lolz`, defines entity `lol` as text, and uses `&lol;` in the document body.

## Control Flow
XML parser tests load the file to exercise inline DTD/entity handling. The expected parse result depends on whether entity expansion is allowed in that test path.

## State And Persistence
The file is static XML data and creates no state.

## Dependencies And Integration Points
It integrates with Hadoop XML parsing and configuration/security hardening tests, especially tests around DTD and entity processing.

## Risks
Entity expansion is security-sensitive. This small fixture is benign, but parser configuration must avoid general XXE-style exposure when external entities are involved.

## Test Signals
Parser tests should either expand the internal entity as expected or reject DTD/entity processing in hardened modes with the intended exception.
