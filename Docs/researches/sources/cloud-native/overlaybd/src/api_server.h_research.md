<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.h -->
# sources/cloud-native/overlaybd/src/api_server.h

Purpose: Declares API server lifecycle functions for the optional live snapshot HTTP service.

APIs and control flow: `start_api_server(ApiServer *&, ImageService *, const std::string &)` allocates and initializes an `ApiServer`; `stop_api_server(ApiServer *)` destroys it. `ApiServer` is forward-declared elsewhere.

State and persistence: Holds no state itself, but the pointer contract transfers heap object ownership to callers.

Dependencies and integration: Included by `image_service.cpp`, which starts the server when `serviceConfig.enable` is true.

Risks and test signals: The header relies on prior declarations of `ApiServer`, `ImageService`, and `std::string`; include order matters. Build failures catch signature drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.h -->
