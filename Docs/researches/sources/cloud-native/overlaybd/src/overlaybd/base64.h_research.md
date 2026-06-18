<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/base64.h -->
# sources/cloud-native/overlaybd/src/overlaybd/base64.h

Purpose: Header-only base64 encode/decode helpers.

APIs and control flow: Defines `base64_chars`, `is_base64`, `base64_encode(BYTE const*, unsigned int)`, and `base64_decode(std::string const&)`. Encoding groups bytes into 3-to-4 chunks and pads with `=`; decoding stops at `=` or non-base64 input and reconstructs bytes.

State and persistence: Stateless pure helpers.

Dependencies and integration: `ImageService::parse_auths` decodes Docker-style `auth` values into `username:password`.

Risks and test signals: Decode silently stops at invalid characters rather than reporting errors. Unit tests should cover padding, empty input, malformed auth, and colon splitting.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/base64.h -->
