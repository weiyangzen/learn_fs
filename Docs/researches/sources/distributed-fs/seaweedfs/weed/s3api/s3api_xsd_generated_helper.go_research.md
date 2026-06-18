# sources/distributed-fs/seaweedfs/weed/s3api/s3api_xsd_generated_helper.go

Purpose: adds a hand-written `Grantee` type to the generated `s3api` XML model. It fills a gap in the generated ACL model by representing the XML/XSI attributes and optional grantee identity fields used inside ACL grants.

Important APIs/types: `Grantee` has XML namespace/type attributes (`xmlns:xsi`, `xsi:type`), a `Type` element, and optional `ID`, `DisplayName`, and `URI` elements.

Control flow: no functions. Encoding/decoding is entirely driven by struct tags and the standard XML encoder.

State and persistence behavior: no persistent state. It affects ACL XML compatibility because `Grant` in the generated file embeds `Grantee`.

Dependencies and integration points: package-local companion for `s3api_xsd_generated.go`, particularly `Grant` and `AccessControlPolicy`. It is used wherever ACL XML is marshaled or unmarshaled.

Risks: because this helper supplies XML namespace attributes manually, tag changes can break ACL interoperability. It is not generated, so schema regeneration could conflict with or supersede it.

Test signals: no direct tests in this subset. ACL handler tests elsewhere should validate canonical user/group grantees.
