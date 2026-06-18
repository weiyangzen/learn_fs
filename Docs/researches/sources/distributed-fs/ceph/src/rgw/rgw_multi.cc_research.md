## sources/distributed-fs/ceph/src/rgw/rgw_multi.cc

Purpose: implements XML parsing support and utility helpers for S3 multipart upload completion.

Important APIs/functions: `RGWMultiPart::xml_end()` extracts `PartNumber` and `ETag`; `RGWMultiCompleteUpload::xml_end()` collects parts into a `std::map<int,std::string>`; `RGWMultiXMLParser::alloc_obj()` maps XML element names to parser objects; `is_v2_upload_id()` recognizes current/legacy v2 upload id prefixes; `RGWUploadPartInfo::dump()` and `generate_test_instances()` support introspection/encoding tests.

Control flow: the XML parser allocates typed nodes while parsing. At each `Part` close, required child nodes are validated and copied. At upload close, all parsed parts are inserted by part number, naturally sorting and overwriting duplicates by map semantics.

State and persistence: parser state is in XML object instances. Upload part info is serializable elsewhere and dumped here for diagnostics.

Dependencies/integration: used by complete-multipart-upload RGW operations; depends on RGW XML parser, object manifest declarations, SAL forward declarations, and multipart upload id constants.

Risks and test signals: `atoi()` silently accepts malformed part-number suffixes. Duplicate part numbers collapse in the map. Tests should include alternate `CompletedMultipartUpload` root compatibility, missing ETag/PartNumber, duplicate parts, invalid numbers, and v2 prefix recognition.
