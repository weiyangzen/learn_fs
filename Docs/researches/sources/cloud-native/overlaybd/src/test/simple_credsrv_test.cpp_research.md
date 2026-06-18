## sources/cloud-native/overlaybd/src/test/simple_credsrv_test.cpp

Purpose: tests loading registry credentials from an HTTP credential service, including timeout behavior.

Important types/functions: `SimpleAuthHandler` implements Photon `HTTPHandler`, returns a JSON body with `"success": true` and nested auth fields, deliberately sleeps before writing to exercise timeout handling. Test `auth.http_server` starts a local HTTP server on `127.0.0.1:19876/auth`, then calls `load_cred_from_http` with timeout values 1 and 2 and checks failure then success.

Control flow: the server is configured with keep-alive and content length, sleeps for one second, writes the body, and the client path parses credentials through image service/config code included directly via `../image_service.cpp`.

State/persistence: no file persistence in the active path; commented code references a local credential file. Dependencies include Photon HTTP/socket/thread, RapidJSON, GTest, localfs, and image service config functions.

Integration points: validates credential retrieval used by image service remote registry access. Risks: timing-based assertion may be flaky on slow systems; fixed port can conflict; returned JSON has blank username/password so it mostly validates request/parse success rather than credential values. Test signal covers timeout branch and success branch.
