# sources/cloud-native/moby/integration-cli/docker_api_images_test.go

## Purpose
Small image API integration coverage for search response content type.

## Important APIs and Types
Defines `TestAPIImagesSearchJSONContentType`.

## Control Flow, State, and Persistence
The test calls image search through the API and asserts JSON content type behavior.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on daemon image search endpoint and possibly network/registry availability depending on environment. Risks include external registry instability and content-type header regressions. It is a narrow HTTP contract signal.
