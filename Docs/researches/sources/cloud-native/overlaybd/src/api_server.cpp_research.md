<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.cpp -->
# sources/cloud-native/overlaybd/src/api_server.cpp

Purpose: Optional HTTP API for live snapshot creation on an existing image device.

APIs and control flow: `ApiHandler::handle_request` parses `/snapshot?dev_id=...&config=...`, validates parameters, locates the `ImageFile` in `ImageService`, calls `ImageFile::create_snapshot`, and writes a JSON success/error body. `parse_params` URL-decodes query pairs. `ApiServer::init` binds a Photon TCP server from `serviceConfig.address`, registers the `/snapshot` handler, and starts the loop.

State and persistence: Mutates active image state via snapshot restack and config rename; keeps a handler params map in memory.

Dependencies and integration: Uses Photon HTTP/socket/URL APIs and `ImageService::find_image_file`.

Risks and test signals: The handler map is not cleared per request, so stale params can survive on reused handler instances. Snapshot API tests should cover missing params, unknown dev_id, bad config, and repeated requests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/api_server.cpp -->
